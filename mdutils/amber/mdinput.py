import typing as tp
import random
from dataclasses import dataclass, asdict
from pathlib import Path
import math

from jinja2 import Environment, FileSystemLoader, select_autoescape

from mdutils.units import FEMTOSECOND_TO_PICOSECOND
from mdutils.dynamics import calc_step_num
from mdutils.ff import ImplicitFF
from mdutils.umbrella import UmbrellaArgs
from mdutils.algorithm import (
    # Baro
    BaseBaro,
    # BerendsenBaro,
    # McBaro,
    # Thermo
    BaseThermo,
    # BerendsenThermo,
    # AndersenThermo,
    # LangevinThermo,
    # OINHThermo,
    # SINHThermo,
    # BussiThermo,
    # Tensionstat
    BaseTension,
)

__all__ = ["AniArgs", "MdArgs", "RunArgs", "MixedSdcgArgs", "MinArgs"]

_TEMPLATES_PATH = Path(__file__).parent.parent.joinpath("templates")

env = Environment(
    loader=FileSystemLoader(_TEMPLATES_PATH),
    autoescape=select_autoescape(),
    trim_blocks=True,
    lstrip_blocks=True,
)

_MAX_32_BIT_INT = 2147483647


@dataclass
class AniArgs:
    use_cuda: bool = True
    use_cuaev: bool = False
    use_amber_neighborlist: bool = False
    double_precision: bool = False
    device_idx: int = -1
    network_idx: int = -1
    model: str = "ani2x"


def parse_umbrella_args(
    args: tp.Optional[tp.Dict[str, tp.Any]] = None,
) -> tp.Dict[str, tp.Any]:
    if args is not None:
        return {
            "umbrella_input_fpath": args["input_fpath"],
            "umbrella_output_fpath": args["output_fpath"],
        }
    else:
        return {}


def parse_torchani_args(
    args: tp.Optional[tp.Dict[str, tp.Any]],
) -> tp.Dict[str, tp.Any]:
    if args is None:
        return {"torchani": False}
    out: tp.Dict[str, tp.Any] = {}
    out["torchani"] = True
    out["ani_use_cuaev"] = ".true." if args["use_cuaev"] else ".false."
    out["ani_use_cuda"] = ".true." if args["use_cuda"] else ".false."
    out["ani_double_precision"] = ".true." if args["double_precision"] else ".false."
    out["ani_device_idx"] = args["device_idx"]
    out["ani_network_idx"] = args["network_idx"]
    out["ani_model"] = args["model"]
    return out


@dataclass
class RunArgs:
    scalars_dump_interval: int = 1
    arrays_dump_interval: int = 1
    restraint_selection: str = ""
    restraint_constant: str = ""
    dump_force: bool = False
    cutoff: float = 8.0
    solvent_model: tp.Optional[ImplicitFF] = None
    umbrella_args: tp.Optional[UmbrellaArgs] = None
    torchani_args: tp.Optional[AniArgs] = None
    random_seed: tp.Optional[int] = None


@dataclass
class MinArgs(RunArgs):
    pass


# Procedure 1: Mixed SteepestDescent + ConjugateGradient
# I believe minimization halts either when the total number of steps
# is exceeded, or when the force rms is smaller than the threshold"""
@dataclass
class MixedSdcgArgs(MinArgs):
    total_minimization_steps: int = 2000
    steepest_descent_fraction: float = 0.1
    initial_step_angstrom: float = 0.01
    force_rms_threshold_kcal_per_angmol: float = 1e-4


# Procedure 2: Md
@dataclass
class MdArgs(RunArgs):
    dump_vel: bool = False
    timestep_fs: float = 1.0
    time_ps: float = 0.0
    restart: bool = False
    shake: bool = True
    temperature_init_kelvin: tp.Optional[float] = None
    thermo: tp.Optional[BaseThermo] = None
    baro: tp.Optional[BaseBaro] = None
    surface_tensionstat: tp.Optional[BaseTension] = None


def _run(
    args: RunArgs,
    template: str,
) -> str:
    template_renderer = env.get_template(template)
    args_dict = asdict(args)
    args_dict.pop("thermo", None)
    args_dict.pop("baro", None)
    args_dict.pop("surface_tensionstat", None)

    solvent = args_dict.pop("solvent_model")
    restraint_selection = args_dict.pop("restraint_selection")
    restraint_constant = args_dict.pop("restraint_constant")
    args_dict.update(parse_umbrella_args(args_dict.pop("umbrella_args")))
    args_dict.update(parse_torchani_args(args_dict.pop("torchani_args")))

    random_seed = args_dict.pop("random_seed")
    if random_seed is None:
        args_dict["random_seed"] = random.randint(0, _MAX_32_BIT_INT - 1)
    else:
        args_dict["random_seed"] = random_seed

    # Restraints
    if restraint_selection:
        args_dict["restraint_selection"] = restraint_selection
        if restraint_constant:
            args_dict["restraint_constant"] = restraint_constant

    # Implicit solvation
    if solvent is not None:
        args_dict["implicit_solvent_model"] = solvent.mdin_idx

    if isinstance(args, MdArgs):
        if args.thermo is not None:
            args_dict["heating"] = (
                args.thermo.temperature_kelvin[0] != args.thermo.temperature_kelvin[1]
            )

        if args.baro is not None:
            if solvent is not None:
                raise ValueError(
                    "Can't perform pressure control in an implicit solvent calculation"
                )
            args_dict["changing_pressure"] = (
                args.baro.pressure_bar[0] != args.baro.pressure_bar[1]
            )

        timestep_fs = args_dict.pop("timestep_fs")
        args_dict["timestep_ps"] = timestep_fs * FEMTOSECOND_TO_PICOSECOND
        args_dict["total_md_steps"] = calc_step_num(
            args_dict.pop("time_ps"), timestep_fs
        )
        return template_renderer.render(
            thermo=args.thermo,
            baro=args.baro,
            surface_tensionstat=args.surface_tensionstat,
            **args_dict,
        )
    elif isinstance(args, MinArgs):
        steepest_descent_fraction = args_dict.pop("steepest_descent_fraction", None)
        if steepest_descent_fraction is not None:
            args_dict["steepest_descent_steps"] = math.ceil(
                steepest_descent_fraction * args_dict["total_minimization_steps"]
            )
        return template_renderer.render(**args_dict)
    else:
        raise ValueError("Unknown procedure type")


# User-facing functions
def mixed_sdcg(args: MixedSdcgArgs) -> str:
    return _run(args, "min-mixed-sdcg.amber.in.jinja")


def md(args: MdArgs) -> str:
    return _run(args, "md.amber.in.jinja")


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
    return _run(args, "md.amber.in.jinja")
