r"""Utilities to deal with amber-style inpcrd files (formatted ascii)"""

from pathlib import Path
from typing import Tuple

import pandas
import numpy as np
from numpy.typing import NDArray


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
