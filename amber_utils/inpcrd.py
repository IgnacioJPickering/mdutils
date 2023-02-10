r"""Utilities to deal with amber-style inpcrd files (formatted ascii)"""

from pathlib import Path
from typing import Tuple, NamedTuple, Optional

import pandas
import numpy as np
from numpy.typing import NDArray

from amber_utils.utils import read_last_line


class AmberInpcrdData(NamedTuple):
    name: str
    atoms_num: int
    coordinates: NDArray[np.float_]
    box_lengths: Optional[NDArray[np.float_]]
    box_angles: Optional[NDArray[np.float_]]


def read_coordinates_and_box(
    inpcrd: Path,
    implicit_input: bool = False,
    infer_implicit_input: bool = True,
) -> Tuple[NDArray[np.float_], Optional[NDArray[np.float_]], Optional[NDArray[np.float_]]]:
    df = pandas.read_csv(inpcrd, skiprows=2, sep=r"\s+", header=None)
    if implicit_input or (infer_implicit_input and ".implicit." in inpcrd.name):
        coordinates = df.values.reshape(-1, 3)
        return coordinates, None, None
    box = df.iloc[-1, :].values
    df.drop(index=(df.shape[0] - 1), axis="rows", inplace=True)
    coordinates = df.values.reshape(-1, 3)
    coordinates = coordinates[~np.isnan(coordinates).any(axis=1)]
    box_lengths = box[:3]
    box_angles = box[3:]
    return coordinates, box_lengths, box_angles


def read_box(
    inpcrd: Path,
    implicit_input: bool = False,
    infer_implicit_input: bool = True,
) -> Tuple[Optional[NDArray[np.float_]], Optional[NDArray[np.float_]]]:
    if implicit_input or (infer_implicit_input and ".implicit." in inpcrd.name):
        return None, None
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


def read_data(inpcrd: Path, implicit_input: bool = False, infer_implicit_input: bool = True) -> AmberInpcrdData:
    name, atoms_num = read_name_and_num_atoms(inpcrd)
    coordinates, box_lengths, box_angles = read_coordinates_and_box(
        inpcrd, implicit_input=implicit_input, infer_implicit_input=infer_implicit_input,
    )
    return AmberInpcrdData(name, atoms_num, coordinates, box_lengths, box_angles)
