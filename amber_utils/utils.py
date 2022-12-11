import os
import math
from pathlib import Path


def get_dynamics_steps(time_ps: float, timestep_fs: float) -> int:
    steps = math.ceil(time_ps * 1000 / timestep_fs)
    return steps


def read_last_line(file_: Path) -> str:
    with open(file_, "rb") as f:
        try:  # catch OSError in case of a one line file
            f.seek(-2, os.SEEK_END)
            while f.read(1) != b"\n":
                f.seek(-2, os.SEEK_CUR)
        except OSError:
            f.seek(0)
        line_ = f.readline().decode()
    return line_
