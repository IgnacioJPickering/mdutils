from typing import Optional, Any
from pathlib import Path
import math

from jinja2 import Environment, FileSystemLoader, select_autoescape

from amber_utils.utils import get_dynamics_steps

_TEMPLATES_PATH = Path(__file__).parent.joinpath("templates")

env = Environment(
    loader=FileSystemLoader(_TEMPLATES_PATH),
    autoescape=select_autoescape(),
    trim_blocks=True,
    lstrip_blocks=True,
)


# how can functions sort of "inherit" some of the arguments of other functions?
# they essentially forward the arguments to the next function
# how does this work?
# what you call is a very specific function, that in turn calls a generic function
# the generic function


def run(
    template: str,
    thermo_output_interval_frames: int,
    trajectory_output_interval_frames: int,
    restrained: bool = False,
    restraint_selection: str = "",
    restraint_constant: float = 1.0,
    write_velocities: bool = False,
    write_forces: bool = False,
    vacuum: bool = False,
    generalized_born: bool = False,
    poisson_boltzmann: bool = False,
    **kwargs: Any,
) -> str:
    if vacuum:
        assert not generalized_born
        assert not poisson_boltzmann
        kwargs["implicit_solvent_model"] = 6
        kwargs["implicit_solvent"] = True
    if generalized_born:
        assert not poisson_boltzmann
        assert not vacuum
        raise ValueError("GB model will be fetched from the prmtop radii in the future")
        kwargs["implicit_solvent_model"] = 6
        kwargs["implicit_solvent"] = True
    if poisson_boltzmann:
        assert not vacuum
        assert not generalized_born
        kwargs["implicit_solvent_model"] = 10
        kwargs["implicit_solvent"] = True
    # if all these are false then a periodic calculation is the default

    template = env.get_template(template)
    return template.render(
        thermo_output_interval_frames=thermo_output_interval_frames,
        trajectory_output_interval_frames=trajectory_output_interval_frames,
        restrained=restrained,
        restraint_selection=restraint_selection,
        restraint_constant=restraint_constant,
        write_velocities=write_velocities,
        write_forces=write_forces,
        **kwargs,
    )


def steepest_descent(
    total_minimization_steps: int = 2000,
    steepest_descent_fraction: float = 0.1,
    **kwargs: Any,
) -> str:
    assert not kwargs.pop("write_velocities", False)
    assert not kwargs.pop("write_forces", False)
    kwargs["total_minimization_steps"] = total_minimization_steps
    kwargs["steepest_descent_steps"] = math.ceil(
        steepest_descent_fraction * total_minimization_steps
    )
    return run(template="minimization.amber.in.jinja", **kwargs)


def single_point(**kwargs: Any) -> str:
    kwargs["template"] = "md.amber.in.jinja"
    assert kwargs.pop("time_ps", None) is None
    assert kwargs.pop("timestep_ps", None) is None
    return dynamics(
        time_ps=0.0,
        thermo_output_interval_frames=1,
        trajectory_output_interval_frames=1,
        **kwargs,
    )


def dynamics(
    template: str,
    time_ps: float,
    timestep_fs: float = 1.0,
    shake: bool = True,
    restart: bool = True,
    write_forces: bool = False,
    write_velocities: bool = False,
    **kwargs: Any,
) -> str:
    kwargs["write_forces"] = write_forces
    kwargs["write_velocities"] = write_velocities
    kwargs["shake"] = shake
    kwargs["timestep_ps"] = timestep_fs * 1e-3
    kwargs["total_md_steps"] = get_dynamics_steps(time_ps, timestep_fs)
    return run(**kwargs)


def dynamics_with_temperature(
    template: str,
    temperature_start_kelvin: float = 300.0,
    temperature_end_kelvin: Optional[float] = None,
    **kwargs: Any,
) -> str:
    if temperature_end_kelvin is None:
        kwargs["heating"] = False
    else:
        kwargs["heating"] = True
        kwargs["temperature_end_kelvin"] = temperature_end_kelvin
    kwargs["temperature_start_kelvin"] = temperature_start_kelvin
    kwargs["template"] = template
    return dynamics(**kwargs)


def dynamics_with_temperature_and_pressure(
    template: str,
    compressibility_inv_megabar: float = 44.6,
    pressure_start_bar: float = 1.0,
    pressure_end_bar: Optional[float] = None,
    inhomogeneous: bool = False,
    **kwargs: Any,
) -> str:
    if kwargs.pop("vacuum", False) or kwargs.pop("implicit_solvent", False):
        raise ValueError(
            "Can't perform pressure control in an implicit solvent calculation"
        )
    if pressure_end_bar is not None:
        raise ValueError("Pressure variation not implemented yet")
    kwargs["pressure_start_bar"] = pressure_start_bar
    kwargs["compressibility_inv_megabar"] = compressibility_inv_megabar
    kwargs["inhomogeneous"] = inhomogeneous
    return dynamics_with_temperature(**kwargs)


def nve(temperture_start_kelvin: float = 300.0, **kwargs: Any) -> str:
    kwargs["template"] = "md.amber.in.jinja"
    kwargs["temperature_start_kelvin"] = temperture_start_kelvin
    return dynamics(**kwargs)


def langevin_nvt(friction_inv_ps: float = 2.0, **kwargs: Any) -> str:
    kwargs["template"] = "langevin-nvt.amber.in.jinja"
    kwargs["friction_inv_ps"] = friction_inv_ps
    return dynamics_with_temperature(**kwargs)


def berendsen_nvt(temperature_tau_ps: float = 1.0, **kwargs: Any) -> str:
    kwargs["template"] = "berendsen-nvt.amber.in.jinja"
    kwargs["temperature_tau_ps"] = temperature_tau_ps
    return dynamics_with_temperature(**kwargs)


def berendsen_npt(
        temperature_tau_ps: float = 1.0, pressure_tau_ps: float = 1.0, **kwargs: Any
) -> str:
    kwargs["template"] = "berendsen-npt.amber.in.jinja"
    kwargs["temperature_tau_ps"] = temperature_tau_ps
    kwargs["pressure_tau_ps"] = pressure_tau_ps
    return dynamics_with_temperature_and_pressure(**kwargs)
