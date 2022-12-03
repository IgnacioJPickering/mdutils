r"""Utilities to deal with amber-style inpcrd files (formatted ascii)"""

from pathlib import Path
from typing import Tuple, NamedTuple

import pandas
import numpy as np
from numpy.typing import NDArray

from amber_utils.utils import read_last_line


class AmberInpcrdData(NamedTuple):
    name: str
    atoms_num: int
    coordinates: NDArray[np.float_]
    box_lengths: NDArray[np.float_]
    box_angles: NDArray[np.float_]


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


def read_name_and_num_atoms(inpcrd: Path) -> Tuple[str, int]:
    with open(inpcrd, "r") as f:
        for j, line in enumerate(f.readlines()):
            if j == 0:
                name = line.strip()
            elif j == 1:
                atoms_num = int(line.strip())
            else:
                break
    return name, atoms_num


def read_data(inpcrd: Path) -> AmberInpcrdData:
    name, atoms_num = read_name_and_num_atoms(inpcrd)
    coordinates, box_lengths, box_angles = read_coordinates_and_box(inpcrd)
    return AmberInpcrdData(name, atoms_num, coordinates, box_lengths, box_angles)
