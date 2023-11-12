import itertools
import typing as tp
import sys
import random
from dataclasses import dataclass, asdict
from pathlib import Path
import math

from jinja2 import Environment, FileSystemLoader, select_autoescape

from amber_utils.ani import AniNeighborlistKind
from amber_utils.units import FEMTOSECOND_TO_PICOSECOND
from amber_utils.utils import get_dynamics_steps
from amber_utils.solvent import SolventModel, mdin_integer
from amber_utils.umbrella import UmbrellaArgs
from amber_utils.thermostats import (
    Thermo,
    BerendsenThermo,
    AndersenThermo,
    LangevinThermo,
    OINHThermo,
    SINHThermo,
    StochasticBerendsenThermo,
)
from amber_utils.barostats import (
    Baro,
    BerendsenBaro,
    McBaro,
)
from amber_utils.surface_tensionstats import SurfaceTensionstat

_TEMPLATES_PATH = Path(__file__).parent.joinpath("templates")

env = Environment(
    loader=FileSystemLoader(_TEMPLATES_PATH),
    autoescape=select_autoescape(),
    trim_blocks=True,
    lstrip_blocks=True,
)

_MAX_32_BIT_INT = 2147483647


@dataclass
class AniArgs:
    neighborlist: AniNeighborlistKind = AniNeighborlistKind.INTERNAL_CELL_LIST
    use_cuda: bool = True
    use_cuaev: bool = False
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
    out["ani_torch_cell_list"] = (
        ".true."
        if args["neighborlist"].value == AniNeighborlistKind.INTERNAL_CELL_LIST.value
        else ".false."
    )
    out["ani_external_neighborlist"] = (
        ".true."
        if args["neighborlist"].value == AniNeighborlistKind.EXTERNAL.value
        else ".false."
    )
    out["ani_device_idx"] = args["device_idx"]
    out["ani_network_idx"] = args["network_idx"]
    out["ani_model"] = args["model"]
    return out


@dataclass
class RunArgs:
    scalars_output_interval_frames: int = 1
    arrays_output_interval_frames: int = 1
    restraint_selection: str = ""
    restraint_constant: str = ""
    write_forces: bool = False
    cutoff: float = 8.0
    solvent_model: SolventModel = SolventModel.EXPLICIT
    umbrella_args: tp.Optional[UmbrellaArgs] = None
    torchani_args: tp.Optional[AniArgs] = None
    random_seed: tp.Optional[int] = None


@dataclass
class MinArgs(RunArgs):
    pass


# Procedure 1: Mixed SteepestDescent + ConjugateGradient
@dataclass
class MixedSdcgArgs(MinArgs):
    """I believe minimization halts either when the total number of steps
    is exceeded, or when the force rms is smaller than the threshold"""

    total_minimization_steps: int = 2000
    steepest_descent_fraction: float = 0.1
    initial_step_angstrom: float = 0.01
    force_rms_threshold_kcal_per_angmol: float = 1e-4


# Procedure 2: Md
@dataclass
class MdArgs(RunArgs):
    write_velocities: bool = False
    timestep_fs: float = 1.0
    time_ps: float = 0.0
    restart: bool = False
    shake: bool = True
    temperature_init_kelvin: tp.Optional[float] = None
    thermo: tp.Optional[Thermo] = None
    baro: tp.Optional[Baro] = None
    surface_tensionstat: tp.Optional[SurfaceTensionstat] = None


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
    if solvent is not SolventModel.EXPLICIT:
        args_dict["implicit_solvent_model"] = mdin_integer(solvent)

    if isinstance(args, MdArgs):
        if args.thermo is not None:
            args_dict["heating"] = (
                args.thermo.temperature_kelvin[0] != args.thermo.temperature_kelvin[1]
            )

        if args.baro is not None:
            if solvent is not SolventModel.EXPLICIT:
                raise ValueError(
                    "Can't perform pressure control in an implicit solvent calculation"
                )
            args_dict["changing_pressure"] = (
                args.baro.pressure_bar[0] != args.baro.pressure_bar[1]
            )

        timestep_fs = args_dict.pop("timestep_fs")
        args_dict["timestep_ps"] = timestep_fs * FEMTOSECOND_TO_PICOSECOND
        args_dict["total_md_steps"] = get_dynamics_steps(
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


# TODO: Validation should be performed by jinja somehow?
def nve(args: MdArgs) -> str:
    if args.baro is not None or args.thermo is not None:
        raise ValueError("No barostat or thermostat arguments expected")
    if args.surface_tensionstat is not None:
        raise ValueError("No surface tension arguments expected")
    return _run(args, "md.amber.in.jinja")


def single_point(args: MdArgs) -> str:
    if (
        args.timestep_fs != 1.0
        or args.time_ps != 0.0
        or args.scalars_output_interval_frames != 1
        or args.arrays_output_interval_frames != 1
    ):
        raise ValueError(
            "Timestep, time, output-freq shouldn't be specified for single-point"
        )
    if args.baro is not None or args.thermo is not None:
        raise ValueError("No barostat or thermostat arguments expected")
    if args.surface_tensionstat is not None:
        raise ValueError("No surface tension arguments expected")
    return _run(args, "md.amber.in.jinja")


def _register_input_maker(thermo: Thermo, baro: tp.Optional[Baro]) -> None:
    if baro is not None:
        name = f"npt_{thermo.name}_{baro.name}"

        def input_maker(
            args: MdArgs,
        ) -> str:
            if not isinstance(args.thermo, type(thermo)) or not isinstance(
                args.baro, type(baro)
            ):
                raise ValueError(
                    f"Expected {thermo} thermo and {baro} baro arguments only"
                )
            if args.surface_tensionstat is not None:
                raise ValueError("No surface tension arguments expected")
            return _run(args, "md.amber.in.jinja")

    else:
        name = f"nvt_{thermo.name}"

        def input_maker(
            args: MdArgs,
        ) -> str:
            if not isinstance(args.thermo, type(thermo)) or args.baro is not None:
                raise ValueError("Expected langevin thermostat arguments only")
                raise ValueError(f"Expected {thermo} thermo arguments only")
            if args.surface_tensionstat is not None:
                raise ValueError("No surface tension arguments expected")
            return _run(args, "md.amber.in.jinja")

    input_maker.__name__ = name
    setattr(sys.modules[__name__], name, input_maker)


for thermo, baro in itertools.product(
    (
        BerendsenThermo,
        AndersenThermo,
        LangevinThermo,
        OINHThermo,
        SINHThermo,
        StochasticBerendsenThermo,
    ),
    (McBaro, BerendsenBaro, None),
):
    _register_input_maker(thermo(), baro() if baro is not None else None)
