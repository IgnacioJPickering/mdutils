import typing as tp
from dataclasses import dataclass

from mdutils.yaml import yamlize, YamlEnum


@yamlize
class Thermo(YamlEnum):
    BERENDSEN = "berendsen"
    ANDERSEN = "andersen"
    LANGEVIN = "langevin"
    OINH = "oinh"
    SINH = "sinh"
    BUSSI = "bussi"
    # TODO: add these?
    # ANDERSEN_MASSIVE for gromacs
    # NOSE_HOOVER = "nosehoover" (nvt in lammps)
    # DIRECT_RESCALE = (temp/rescale) in lammps, how is it different from berendsen?
    # DPD = "dpd" dissipative particle dynamics in lammps
    # CSVR|CSLD = "csvr" csvr lammps? I think this is Bussi, and can be used with
    # langevin dynamics? what does that mean?


@dataclass
class BaseThermo:
    temperature_kelvin: tp.Tuple[float, float] = (300.0, 300.0)

    @property
    def name(self) -> str:
        return self.__class__.__name__.replace("Thermo", "").lower()


@dataclass
class BerendsenThermo(BaseThermo):
    r"""
    AKA "Weak coupling scheme"
    """
    temperature_relax_time_ps: float = 1.0


@dataclass
class AndersenThermo(BaseThermo):
    vel_randomization_step_interval: int = 1000


@dataclass
class LangevinThermo(BaseThermo):
    friction_inv_ps: float = 2.0


@dataclass
class OptimizedIsokineticNoseHooverChainEnsembleThermo(BaseThermo):
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
class StochasticIsokineticNoseHooverRespaThermo(BaseThermo):
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
class BussiThermo(BaseThermo):
    r"""
    AKA Stochastic Berendsen thermostat
    """
    temperature_relax_time_ps: float = 1.0

    @property
    def name(self) -> str:
        return "bussi"


StochasticBerendsenThermo = BussiThermo
