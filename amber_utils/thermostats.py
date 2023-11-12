import typing as tp
from dataclasses import dataclass


@dataclass
class Thermo:
    temperature_kelvin: tp.Tuple[float, float] = (300.0, 300.0)

    @property
    def name(self) -> str:
        return self.__class__.__name__.replace("Thermo", "").lower()


@dataclass
class BerendsenThermo(Thermo):
    r"""
    AKA "Weak coupling scheme"
    """
    temperature_relax_time_ps: float = 1.0


@dataclass
class AndersenThermo(Thermo):
    vel_randomization_step_interval: int = 1000


@dataclass
class LangevinThermo(Thermo):
    friction_inv_ps: float = 2.0


@dataclass
class OptimizedIsokineticNoseHooverChainEnsembleThermo(Thermo):
    """
    AKA OINH thermostat

    Implemented for "multiple timestep methods" (3D rism and respa)
    for respa it allows 16 fs (nrespa = 16, dt = 0.001)
    For 3d-rism 8 fs (dt = 0.001, rismrespa = 8)

    Writes 2 additional files for restarts
    """
    friction_inv_ps: float = 2.0
    substep_num: int = 1
    # TODO: default for idistr unknown
    vel_distribution_accumulation_step_interval: int = 10  # idistr

    @property
    def name(self) -> str:
        return "oinh"


OINHThermo = OptimizedIsokineticNoseHooverChainEnsembleThermo


@dataclass
class StochasticIsokineticNoseHooverRespaThermo(Thermo):
    r"""
    AKA SINH thermostat
    Note that the particles are canonical in this thermostat, but the velocities
    are not canonical, and the temperature appears to be less than the actual
    temperature of the system
    """
    additional_dof_num: int = 1
    dof_mass: float = 1.0

    @property
    def name(self) -> str:
        return "sinh"


SINHThermo = StochasticIsokineticNoseHooverRespaThermo


@dataclass
class StochasticBerendsenThermo(Thermo):
    r"""
    AKA Bussi thermostat or SBerendsen thermostat
    """
    temperature_relax_time_ps: float = 1.0

    @property
    def name(self) -> str:
        return "sberendsen"


BussiThermo = StochasticBerendsenThermo
SBerendsenThermo = StochasticBerendsenThermo
