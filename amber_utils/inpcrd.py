r"""Utilities to deal with amber-style inpcrd files (formatted ascii)"""
import itertools
import typing as tp
from dataclasses import dataclass
from pathlib import Path
import os

import numpy as np
from numpy.typing import NDArray

from amber_utils.box import BoxParams


@dataclass
class AmberInpcrdMetadata:
    name: str
    atoms_num: int
    box_params: tp.Optional[BoxParams] = None

    @property
    def box_lengths(self) -> NDArray[np.float_]:
        if self.box_params is None:
            raise ValueError("There should be box parameters to get box lengths")
        return self.box_params.lengths

    @property
    def box_angles(self) -> NDArray[np.float_]:
        if self.box_params is None:
            raise ValueError("There should be box parameters to get box angles")
        return self.box_params.angles

    @property
    def has_box(self) -> bool:
        return self.box_params is not None


# Note that to correctly load the metadata from the inpcrd file, it *must* be
# known if the structure has a box or not, otherwise the whole file will have
# to be read, and whether the box is there or not is inferred from the number
# of atoms
def load_metadata(inpcrd: Path, has_box: bool) -> AmberInpcrdMetadata:
    with open(inpcrd, mode="rb") as f:
        f.seek(0)
        name, atoms_num = list(itertools.islice(f, 0, 2))
        if has_box:
            f.seek(-80, os.SEEK_END)
            box = f.readlines()[-1].decode("ascii").split()
            box_params = BoxParams(
                np.array(box[:3], dtype=np.float64),
                (float(box[3]), float(box[4]), float(box[5])),
            )
        else:
            box_params = None
    return AmberInpcrdMetadata(
        name.decode("ascii"),
        int(atoms_num.decode("ascii")),
        box_params,
    )


@dataclass
class AmberInpcrd:
    name: str
    coordinates: NDArray[np.float_]
    box_params: tp.Optional[BoxParams] = None

    @property
    def atoms_num(self) -> int:
        return self.coordinates.shape[0]

    @property
    def velocities(self) -> None:
        return None

    @property
    def forces(self) -> None:
        return None

    @property
    def box_lengths(self) -> NDArray[np.float_]:
        if self.box_params is None:
            raise ValueError("There should be box parameters to get box lengths")
        return self.box_params.lengths

    @property
    def box_angles(self) -> NDArray[np.float_]:
        if self.box_params is None:
            raise ValueError("There should be box parameters to get box angles")
        return self.box_params.angles

    @property
    def has_box(self) -> bool:
        return self.box_params is not None


def _read_name_and_num_atoms(inpcrd: Path) -> tp.Tuple[str, int]:
    with open(inpcrd, mode="r", encoding="utf-8") as f:
        for j, line in enumerate(f):
            if j == 0:
                name = line.strip()
            elif j == 1:
                atoms_num = int(line.strip())
            else:
                break
    return name, atoms_num


def load(
    inpcrd: Path,
) -> AmberInpcrd:
    # import here to improve startup time
    import pandas  # noqa
    name, atoms_num = _read_name_and_num_atoms(inpcrd)
    df = pandas.read_csv(inpcrd, skiprows=2, sep=r"\s+", header=None)
    floats = df.values.reshape(-1, 3)
    coordinates = floats[:atoms_num]
    box = floats[atoms_num:]

    box_params: tp.Optional[BoxParams]
    if box.shape[0] == 0 or np.isnan(box).any():
        box_params = None
    else:
        box_params = BoxParams(box[0, :], box[1, :])
    return AmberInpcrd(
        name=name,
        coordinates=coordinates,
        box_params=box_params,
    )
