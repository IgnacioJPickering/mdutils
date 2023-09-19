import typing as tp
from dataclasses import dataclass, asdict
from pathlib import Path
import math

from jinja2 import Environment, FileSystemLoader, select_autoescape

from amber_utils.ani import AniNeighborlistKind
from amber_utils.units import FEMTOSECOND_TO_PICOSECOND
from amber_utils.options import Step
from amber_utils.utils import get_dynamics_steps
from amber_utils.solvent import SolventModel, mdin_integer

_TEMPLATES_PATH = Path(__file__).parent.joinpath("templates")

env = Environment(
    loader=FileSystemLoader(_TEMPLATES_PATH),
    autoescape=select_autoescape(),
    trim_blocks=True,
    lstrip_blocks=True,
)


@dataclass
class UmbrellaArgs:
    output_fpath: Path
    restraints_fpath: Path


@dataclass
class AniArgs:
    neighborlist: AniNeighborlistKind = AniNeighborlistKind.INTERNAL_CELL_LIST
    use_cuda: bool = True
    double_precision: bool = False
    device_idx: int = -1
    network_idx: int = -1
    model: str = "ani2x"


def parse_umbrella_args(
    args: tp.Optional[tp.Dict[str, tp.Any]] = None,
) -> tp.Dict[str, tp.Any]:
    if args is not None:
        return {
            "umbrella_restraints_fpath": args["restraints_fpath"],
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
    out["ani_use_cuda"] = ".true." if args["use_cuda"] else ".false."
    out["ani_double_precision"] = ".true." if args["double_precision"] else ".false."
    out["ani_torch_cell_list"] = (
        ".true."
        if args["neighborlist"] is AniNeighborlistKind.INTERNAL_CELL_LIST
        else ".false."
    )
    out["ani_external_neighborlist"] = (
        ".true." if args["neighborlist"] is AniNeighborlistKind.EXTERNAL else ".false."
    )
    out["ani_device_idx"] = args["device_idx"]
    out["ani_network_idx"] = args["network_idx"]
    out["ani_model"] = args["model"]
    return out


@dataclass
class CommonArgs:
    thermo_output_interval_frames: int = 1
    trajectory_output_interval_frames: int = 1
    restraint_selection: str = ""
    restraint_constant: str = ""
    write_velocities: bool = False
    write_forces: bool = False
    solvent_model: SolventModel = SolventModel.EXPLICIT
    umbrella_args: tp.Optional[UmbrellaArgs] = None
    torchani_args: tp.Optional[AniArgs] = None


@dataclass
class MdArgs(CommonArgs):
    timestep_fs: float = 1.0
    time_ps: float = 0.0
    restart: bool = False
    shake: bool = True


@dataclass
class NvtArgs(MdArgs):
    temperature_kelvin: tp.Tuple[float, float] = (300.0, 300.0)


@dataclass
class NptArgs(NvtArgs):
    pressure_bar: tp.Tuple[float, float] = (1.0, 1.0)
    compressibility_inv_megabar: float = 44.6
    inhomogeneous: bool = False


@dataclass
class NveArgs(MdArgs):
    temperature_init_kelvin: float = 300.0


# Mixed SteepestDescent + ConjugateGradient
@dataclass
class MixedSdcgArgs(CommonArgs):
    total_minimization_steps: int = 2000
    steepest_descent_fraction: float = 0.1


@dataclass
class NvtLangevinArgs(NvtArgs):
    friction_inv_ps: float = 2.0


@dataclass
class NvtBerendsenArgs(NvtArgs):
    temperature_tau_ps: float = 1.0


@dataclass
class NptBerendsenBbaroArgs(NptArgs):
    temperature_tau_ps: float = 1.0
    pressure_tau_ps: float = 1.0


def _run(
    args: CommonArgs,
    template: str,
    step_kind: Step,
) -> str:
    template_renderer = env.get_template(template)
    args_dict = asdict(args)
    solvent = args_dict.pop("solvent_model")
    restraint_selection = args_dict.pop("restraint_selection")
    restraint_constant = args_dict.pop("restraint_constant")
    args_dict.update(parse_umbrella_args(args_dict.pop("umbrella_args")))
    args_dict.update(parse_torchani_args(args_dict.pop("torchani_args")))

    # Restraints
    if restraint_selection:
        args_dict["restraint_selection"] = restraint_selection
        if restraint_constant:
            args_dict["restraint_constant"] = restraint_constant

    # Implicit solvation
    if solvent is not SolventModel.EXPLICIT:
        args_dict["implicit_solvent_model"] = mdin_integer(solvent)

    temperature_kelvin = args_dict.pop("temperature_kelvin", None)
    if temperature_kelvin is not None:
        if temperature_kelvin[0] != temperature_kelvin[1]:
            args_dict["temperature_start_kelvin"] = temperature_kelvin[0]
            args_dict["temperature_end_kelvin"] = temperature_kelvin[1]
            args_dict["heating"] = True
        else:
            args_dict["temperature_start_kelvin"] = temperature_kelvin[0]
            args_dict["heating"] = False

    pressure_bar = args_dict.pop("pressure_bar", None)
    if pressure_bar is not None:
        if solvent is not SolventModel.EXPLICIT:
            raise ValueError(
                "Can't perform pressure control in an implicit solvent calculation"
            )
        if pressure_bar[0] != pressure_bar[1]:
            args_dict["pressure_start_bar"] = pressure_bar[0]
            args_dict["pressure_end_bar"] = pressure_bar[1]
            args_dict["changing_pressure"] = True
        else:
            args_dict["pressure_end_kelvin"] = pressure_bar[0]
            args_dict["changing_pressure"] = False

    steepest_descent_fraction = args_dict.pop("steepest_descent_fraction", None)
    if steepest_descent_fraction is not None:
        args_dict["steepest_descent_steps"] = math.ceil(
            steepest_descent_fraction * args_dict["total_minimization_steps"]
        )

    if step_kind is Step.MD:
        timestep_fs = args_dict.pop("timestep_fs")
        args_dict["timestep_ps"] = timestep_fs * FEMTOSECOND_TO_PICOSECOND
        args_dict["total_md_steps"] = get_dynamics_steps(
            args_dict.pop("time_ps"), timestep_fs
        )
    elif step_kind is Step.MIN:
        if args.write_velocities:
            raise ValueError("Velocities should not be written during minimization")

    return template_renderer.render(**args_dict)


def _dynamics(args: MdArgs, template: str) -> str:
    return _run(args, template=template, step_kind=Step.MD)


def _dynamics_with_temperature(
    args: NvtArgs,
    template: str,
) -> str:
    return _dynamics(args, template)


def _dynamics_with_temperature_and_pressure(
    args: NptArgs,
    template: str,
) -> str:
    return _dynamics_with_temperature(args, template)


# User-facing functions
def mixed_sdcg(args: MixedSdcgArgs) -> str:
    return _run(args, "min-mixed-sdcg.amber.in.jinja", step_kind=Step.MIN)


def single_point(args: MdArgs) -> str:
    if (
        args.timestep_fs != 1.0
        or args.time_ps != 0.0
        or args.thermo_output_interval_frames != 1
        or args.trajectory_output_interval_frames != 1
    ):
        raise ValueError(
            "Timestep, time or output frequency should not be specified for single-point"
        )
    return _dynamics(args, "md.amber.in.jinja")


def nve(args: NveArgs) -> str:
    return _dynamics(args, "md.amber.in.jinja")


def nvt_langevin(
    args: NvtLangevinArgs,
) -> str:
    return _dynamics_with_temperature(args, "nvt-langevin.amber.in.jinja")


def nvt_berendsen(
    args: NvtBerendsenArgs,
) -> str:
    return _dynamics_with_temperature(args, "nvt-berendsen.amber.in.jinja")


def npt_berendsen_bbaro(
    args: NptBerendsenBbaroArgs,
) -> str:
    return _dynamics_with_temperature_and_pressure(
        args, "npt-berendsen-bbaro.amber.in.jinja"
    )
