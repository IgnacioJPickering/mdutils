import math
from enum import Enum
from mdutils.units import PICOSECOND_TO_FEMTOSECOND, FEMTOSECOND_TO_PICOSECOND


class Backend(Enum):
    ASE = "ase"
    SANDER = "sander"
    PMEMD = "pmemd"
    OPENMM = "openmm"
    LAMMPS = "lammps"
    GROMACS = "gromacs"


class Step(Enum):
    MD = "md"
    MIN = "min"


class Ensemble(Enum):
    NVT = "nvt"
    NPT = "npt"
    NVE = "nve"


class InitialVelocities(Enum):
    MAXWELL_BOLTZMANN = "maxwell-boltzmann"
    FROM_STRUCTURE = "vel-from-structure"
    ZERO = "zero-vel"


def calc_step_num(time_ps: float, timestep_fs: float) -> int:
    steps = math.ceil(time_ps * PICOSECOND_TO_FEMTOSECOND / timestep_fs)
    return steps


def calc_time_ps(steps: int, timestep_fs: float) -> float:
    return float(steps * timestep_fs * FEMTOSECOND_TO_PICOSECOND)
