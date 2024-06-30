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
    steps = math.ceil(time_ps * PICOSECOND_TO_FEMTOSECOND / timestep_fs)
    return steps


def calc_time_ps(steps: int, timestep_fs: float) -> float:
    return float(steps * timestep_fs * FEMTOSECOND_TO_PICOSECOND)


def output_freq_to_step_interval(
    freq: str, timestep_fs: tp.Optional[float] = None, verbose: bool = False
) -> int:
    if re.match(r"[1-9][0-9]* */ *(us|ns|ps|fs)", freq):
        if timestep_fs is None:
            raise ValueError("Timestep should be specified for time-style frequency")
        num, time_units = freq.split("/")
        factor = {"fs": 1000**2, "ps": 1000, "ns": 1, "us": 1 / 1000}
        outputs_per_ns = int(num) * factor[time_units]
        timesteps_per_ns = (1 / timestep_fs) * 1000 * 1000
        step_interval = int(timesteps_per_ns // outputs_per_ns)
        if step_interval == 0:
            step_interval = 1
            if verbose:
                print(
                    "Requested write freq too high, will write every timestep instead"
                )
    elif re.match(r"1 */ *[1-9][0-9]*", freq):
        step_interval = int(freq.split("/")[1])
    elif freq == "every-step":
        step_interval = 1
    else:
        raise ValueError(
            "Bad format, should be: 'every-step', '1/steps' or 'outputs/(ns|ps|fs)'"
        )
    return step_interval
