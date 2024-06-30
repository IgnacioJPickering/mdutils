import math
from enum import Enum
import re
import typing as tp

from mdutils.units import PICOSECOND_TO_FEMTOSECOND, FEMTOSECOND_TO_PICOSECOND


__all__ = ["Backend", "Step", "Ensemble", "InitVel", "calc_step_num", "calc_time_ps"]


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


class InitVel(Enum):
    MAXWELL_BOLTZMANN = "maxwell-boltzmann"
    FROM_STRUCTURE = "vel-from-structure"
    ZERO = "zero-vel"


def calc_step_num(time_ps: float, timestep_fs: float) -> int:
    if time_ps < 0:
        raise ValueError("time_ps should be > 0")
    if timestep_fs <= 0:
        raise ValueError("timestep_fs should be >= 0")
    return math.ceil(time_ps * PICOSECOND_TO_FEMTOSECOND / timestep_fs)


def calc_time_ps(steps: int, timestep_fs: float) -> float:
    if steps < 0:
        raise ValueError("steps should be > 0")
    if timestep_fs < 0:
        raise ValueError("timestep_fs should be > 0")
    return float(steps * timestep_fs * FEMTOSECOND_TO_PICOSECOND)


_DUMPS_PER_TIME = re.compile(r"^[1-9]\d*\s*/\s*[unpf]s$")
_DUMPS_PER_STEP = re.compile(r"^1\s*/\s*[1-9]\d*$")
_EVERY_STEP = re.compile(r"^every-step$")
_FACTOR = {"fs": 1.0e6, "ps": 1.0e3, "ns": 1.0, "us": 1.0e-3}


def dump_rate_to_step_interval(
    rate: str, timestep_fs: tp.Optional[float] = None
) -> int:
    r"""
    Given a "dump rate" in any of the following forms:
    - '1/steps'
    - 'dumps/(us|ns|ps|fs)'
    - 'every-step'

    Calculates the number of steps between two dumps (minimum is 1)

    If the format is 'dumps/(us|ns|ps|fs)' then the timestep in fs must also
    be specified
    """
    if _DUMPS_PER_TIME.match(rate):
        if timestep_fs is None:
            raise ValueError(
                "Timestep should be specified for dumps-per-timeunit style freq"
            )
        num, time_units = rate.split("/")
        dumps_per_ns = int(num) * _FACTOR[time_units.strip()]
        timesteps_per_ns = (1 / timestep_fs) * 1000 * 1000
        step_interval = max(1, int(timesteps_per_ns // dumps_per_ns))
    elif _DUMPS_PER_STEP.match(rate):
        step_interval = max(1, int(rate.split("/")[1]))
    elif _EVERY_STEP.match(rate):
        step_interval = 1
    else:
        raise ValueError(
            "Bad format, should be: 'every-step', '1/steps' or 'dumps/(us|ns|ps|fs)'"
        )
    return step_interval
