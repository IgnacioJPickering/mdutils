import os
import typing as tp
import re
import math
from pathlib import Path

from amber_utils.units import PICOSECOND_TO_FEMTOSECOND


def get_dynamics_steps(time_ps: float, timestep_fs: float) -> int:
    steps = math.ceil(time_ps * PICOSECOND_TO_FEMTOSECOND / timestep_fs)
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


# Each simulation step a new runner is constructed, and a completely new
# attacher is passed to the runner
def output_freq_to_frame_interval(
    freq: str, timestep_fs: tp.Optional[float] = None, verbose: bool = False
) -> int:
    if re.match(r"[1-9][0-9]* */ *(us|ns|ps|fs)", freq):
        if timestep_fs is None:
            raise ValueError("Timestep should be specified for time-style frequency")
        num, time_units = freq.split("/")
        factor = {"fs": 1000**2, "ps": 1000, "ns": 1, "us": 1 / 1000}
        outputs_per_ns = int(num) * factor[time_units]
        timesteps_per_ns = (1 / timestep_fs) * 1000 * 1000
        frame_interval = int(timesteps_per_ns // outputs_per_ns)
        if frame_interval == 0:
            frame_interval = 1
            if verbose:
                print(
                    "Requested write freq too high, will write every timestep instead"
                )
    elif re.match(r"1 */ *[1-9][0-9]*", freq):
        frame_interval = int(freq.split("/")[1])
    elif freq == "every-step":
        frame_interval = 1
    else:
        raise ValueError(
            "Incorrect freq format, should be'every-step', '1 / frames' or 'outputs / (ns|ps|fs)'"
        )
    return frame_interval
