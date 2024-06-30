r"""
Algorithms for MD: Thermostats, Barostats, Tensionstats and optimizers.
Parameters and defaults for the different schemes.
"""

import typing as tp
from dataclasses import dataclass
from enum import Enum

from mdutils.geometry import Scaling, Plane

__all__ = ["OptimizerKind", "ThermoKind", "BaroKind", "TensionKind"]


# Optimizers
class OptimizerKind(Enum):
    LBFGS = "lbfgs"
    BFGS = "bfgs"
    FIRE = "fire"
    STEEPEST_DESCENT = "steepest-descent"


# Thermostats
# TODO: add these?
# ANDERSEN_MASSIVE for gromacs
# NOSE_HOOVER = "nosehoover" (nvt in lammps)
# DIRECT_RESCALE = (temp/rescale) in lammps, how is it different from berendsen?
# DPD = "dpd" dissipative particle dynamics in lammps
# CSVR|CSLD = "csvr" csvr lammps? I think this is Bussi, and can be used with
# langevin dynamics? what does that mean?
class ThermoKind(Enum):
    BERENDSEN = "berendsen"
    ANDERSEN = "andersen"
    LANGEVIN = "langevin"
    OINH = "oinh"
    SINH = "sinh"
    BUSSI = "bussi"


@dataclass
class BaseThermo:
    name: tp.ClassVar[str] = ""
    temperature_kelvin: tp.Tuple[float, float] = (300.0, 300.0)


@dataclass
class BerendsenThermo(BaseThermo):
    r"""
    AKA "Weak coupling scheme"
    """

    name: tp.ClassVar[str] = "berendsen"
    temperature_relax_time_ps: float = 1.0


@dataclass
class AndersenThermo(BaseThermo):
    name: tp.ClassVar[str] = "andersen"
    vel_randomization_step_interval: int = 1000


@dataclass
class LangevinThermo(BaseThermo):
    name: tp.ClassVar[str] = "langevin"
    friction_inv_ps: float = 2.0


@dataclass
class OINHThermo(BaseThermo):
    """
    Optimized Isokinetic Nose-Hoover Chain Ensemble Thermo
    Implemented for "multiple timestep methods" (3D rism and respa)
    for respa it allows 16 fs (nrespa = 16, dt = 0.001)
    For 3d-rism 8 fs (dt = 0.001, rismrespa = 8)

    Writes 2 additional files for restarts
    """

    name: tp.ClassVar[str] = "oinh"
    friction_inv_ps: float = 2.0
    substep_num: int = 1
    # TODO: default for idistr unknown
    vel_distribution_accumulation_step_interval: int = 10  # idistr


@dataclass
class SINHThermo(BaseThermo):
    r"""
    Stochastic Isokinetic Nose-Hoover Respa Thermo
    Note that the particles are canonical in this thermostat, but the velocities
    are not canonical, and the temperature appears to be less than the actual
    temperature of the system
    """

    name: tp.ClassVar[str] = "sinh"
    additional_dof_num: int = 1
    dof_mass: float = 1.0


@dataclass
class BussiThermo(BaseThermo):
    r"""
    AKA Stochastic Berendsen
    """

    name: tp.ClassVar[str] = "bussi"
    temperature_relax_time_ps: float = 1.0


# Barostats
# TODO: add these?
# BUSSI ? C-rescale (stochastic berendsen barostat) gromacs
# MTTK for gromacs
# PARRINELLO_RAHMAN = "parrinellorahman" for ase and gromacs
# NOSE_HOOVER = "nosehoover" for lammps and ase
# LAMMPS does not have MC barostat
class BaroKind(Enum):
    MC = "mc-baro"
    BERENDSEN = "berendsen-baro"


@dataclass
class BaseBaro:
    name: tp.ClassVar[str] = ""
    pressure_bar: tp.Tuple[float, float] = (1.0, 1.0)
    scaling: Scaling = Scaling.ISOTROPIC


@dataclass
class BerendsenBaro(BaseBaro):
    name: tp.ClassVar[str] = "berendsen-baro"
    pressure_relax_time_ps: float = 1.0
    compressibility_inv_megabar: float = 44.6


@dataclass
class McBaro(BaseBaro):
    name: tp.ClassVar[str] = "mc-baro"
    attempts_step_interval: int = 100


# Surface tension
class TensionKind(Enum):
    MC = "mc-tension"


@dataclass
class BaseTension:
    r"""
    Base Surface Tensionstat
    """

    tension_dyne_per_cm: float = 1.0
    plane: Plane = Plane.XY
    interface_num: int = 2


@dataclass
class McTension(BaseTension):
    name: tp.ClassVar[str] = "mc-tension"
    attempts_step_interval: int = 100
