r"""Utilities to deal with amber-style inpcrd files (formatted ascii)"""

from pathlib import Path
from typing import Tuple

import pandas
import numpy as np
from numpy.typing import NDArray

from amber_utils.utils import read_last_line


def read_coordinates_and_box(
    inpcrd: Path,
) -> Tuple[NDArray[np.float_], NDArray[np.float_], NDArray[np.float_]]:
    df = pandas.read_csv(inpcrd, skiprows=2, sep=r"\s+", header=None)
    box = df.iloc[-1, :].values
    df.drop(index=(df.shape[0] - 1), axis="rows", inplace=True)
    coordinates = df.values.reshape(-1, 3)
    box_lengths = box[:3]
    box_angles = box[3:]
    return coordinates, box_lengths, box_angles


def read_box(inpcrd: Path) -> Tuple[NDArray[np.float_], NDArray[np.float_]]:
    last_line = read_last_line(inpcrd)
    box = [float(fl) for fl in last_line.split()]
    box_lengths = np.array(box[:3])
    box_angles = np.array(box[3:])
    return box_lengths, box_angles
