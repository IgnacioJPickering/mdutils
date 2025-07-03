import typing as tp
import random
from dataclasses import dataclass
from pathlib import Path
import math

import jinja2

from mdutils.units import FEMTOSECOND_TO_PICOSECOND, PICOSECOND_TO_NANOSECOND
from mdutils.dynamics import calc_step_num
from mdutils.ff import ImplicitFF
from mdutils.umbrella import UmbrellaArgs
from mdutils.algorithm import BaseBaro, BaseThermo, BaseTension

__all__ = ["AniArgs", "MdArgs", "RunArgs", "MixedSdcgArgs", "MinArgs"]

_TEMPLATES_PATH = Path(__file__).parent.parent.joinpath("templates")

env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(_TEMPLATES_PATH),
    undefined=jinja2.StrictUndefined,
    autoescape=jinja2.select_autoescape(),
    trim_blocks=True,
    lstrip_blocks=True,
)


@dataclass
class AniArgs:
    use_cuda: bool = True
    use_cuaev: bool = False
    use_amber_neighborlist: bool = False
    use_all_amber_nonbond: bool = False
    double_precision: bool = False
    device_idx: int = -1
    network_idx: int = -1
    model: str = "ani2x"


@dataclass
class CartRestraints:
    selection: str = ""
    constant: float = 1.0


@dataclass
class FrozenAtoms:
    selection: str = ""


@dataclass
class RunArgs:
    scalars_dump_interval: int = 1
    arrays_dump_interval: int = 1
    restart_dump_interval: tp.Optional[int] = None
    dump_force: bool = False
    input_cutoff: tp.Optional[float] = None
    input_random_seed: tp.Optional[int] = None
    implicit_solvent: tp.Optional[ImplicitFF] = None
    umbrella: tp.Optional[UmbrellaArgs] = None
    cart_restraints: tp.Optional[CartRestraints] = None
    frozen_atoms: tp.Optional[FrozenAtoms] = None
    ani: tp.Optional[AniArgs] = None
    use_netcdf: bool = True

    @property
    def random_seed(self) -> int:
        if self.input_random_seed is None:
            return random.randint(0, 2**31 - 2)
        return self.input_random_seed

    @property
    def cutoff(self) -> float:
        if self.input_cutoff is None:
            if self.implicit_solvent:
                return 9999.0
            # TODO: Correctly select cutoff for ani models
            return 8.0
        return self.input_cutoff


@dataclass
class MinArgs(RunArgs):
    @property
    def do_heating(self) -> bool:
        return False

    @property
    def dump_vel(self) -> bool:
        return False


# Procedure 1: Mixed SteepestDescent + ConjugateGradient
# I believe minimization halts either when the total number of steps
# is exceeded, or when the force rms is smaller than the threshold"""
@dataclass
class MixedSdcgArgs(MinArgs):
    total_minimization_steps: int = 2000
    steepest_descent_fraction: float = 0.1
    initial_step_ang: float = 0.01
    force_rms_threshold_kcal_per_angmol: float = 1e-4

    @property
    def steepest_descent_steps(self) -> int:
        return math.ceil(self.steepest_descent_fraction * self.total_minimization_steps)


# Procedure 2: Md
@dataclass
class MdArgs(RunArgs):
    dump_vel: bool = False
    input_timestep_fs: tp.Optional[float] = None
    time_ps: float = 10.0
    restart: bool = False
    shake: bool = True
    temperature_init_kelvin: tp.Optional[float] = None
    thermo: tp.Optional[BaseThermo] = None
    baro: tp.Optional[BaseBaro] = None
    surface_tensionstat: tp.Optional[BaseTension] = None
    remd_time_interval_ps: float = 0.0  # 1.0 or 2.0 are typical values

    def __post_init__(self) -> None:
        if self.baro is not None and self.implicit_solvent is not None:
            raise ValueError("Implicit solvent not supported with NPT dynamics")
        if self.restart and self.temperature_init_kelvin is not None:
            raise ValueError("temperature_init_kelvin has no effect for restarts")

    @property
    def actual_temperature_init_kelvin(self) -> float:
        if self.temperature_init_kelvin is not None:
            return self.temperature_init_kelvin
        if self.thermo is not None:
            return self.thermo.temperature_kelvin[0]
        return 0.0

    @property
    def do_heating(self) -> bool:
        if self.thermo is None:
            return False
        return self.thermo.temperature_kelvin[0] != self.thermo.temperature_kelvin[1]

    @property
    def do_pressure_change(self) -> bool:
        if self.baro is None:
            return False
        return self.baro.pressure_bar[0] != self.baro.pressure_bar[1]

    @property
    def timestep_fs(self) -> float:
        if self.input_timestep_fs is None:
            return 2.0 if self.shake else 1.0
        return self.input_timestep_fs

    @property
    def time_ns(self) -> float:
        return self.time_ps * PICOSECOND_TO_NANOSECOND

    @property
    def timestep_ps(self) -> float:
        return self.timestep_fs * FEMTOSECOND_TO_PICOSECOND

    @property
    def remd_exchange_num(self) -> int:
        if self.remd_time_interval_ps == 0.0:
            return 1
        return math.ceil(self.time_ps / self.remd_time_interval_ps)

    @property
    def total_md_steps(self) -> int:
        return calc_step_num(self.time_ps, self.timestep_fs)

    @property
    def md_steps_per_remd_exchange(self) -> int:
        return calc_step_num(self.remd_time_interval_ps, self.timestep_fs)


# User-facing functions
def mixed_sdcg(args: MixedSdcgArgs) -> str:
    return env.get_template("min-mixed-sdcg.mdin.jinja").render(config=args)


def md(args: MdArgs) -> str:
    return env.get_template("md.mdin.jinja").render(config=args)


def single_point(args: MdArgs) -> str:
    if (
        args.timestep_fs != 1.0
        or args.time_ps != 0.0
        or args.scalars_dump_interval != 1
        or args.arrays_dump_interval != 1
    ):
        raise ValueError(
            "Timestep, time, output-freq shouldn't be specified for single-point"
        )
    if args.baro is not None or args.thermo is not None:
        raise ValueError("No barostat or thermostat arguments expected")
    if args.surface_tensionstat is not None:
        raise ValueError("No surface tension arguments expected")
    return env.get_template("md.mdin.jinja").render(config=args)
