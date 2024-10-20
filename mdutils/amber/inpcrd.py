r"""
Utilities to deal with amber-style inpcrd files and their metadata (formatted ascii)
"""

import typing_extensions as tpx
import itertools
import typing as tp
from dataclasses import dataclass
from pathlib import Path
import os

import numpy as np
from numpy.typing import NDArray

from mdutils.geometry import BoxParams

__all__ = ["Inpcrd", "InpcrdMeta"]


@dataclass
class InpcrdMeta:
    name: str
    atoms_num: int
    box_params: tp.Optional[BoxParams] = None

    @property
    def box_lengths(self) -> NDArray[np.float64]:
        if self.box_params is None:
            raise ValueError("There should be box parameters to get box lengths")
        return self.box_params.lengths

    @property
    def box_angles(self) -> NDArray[np.float64]:
        if self.box_params is None:
            raise ValueError("There should be box parameters to get box angles")
        return self.box_params.angles

    @property
    def has_box(self) -> bool:
        return self.box_params is not None

    @classmethod
    def load(cls, path: Path, has_box: bool) -> tpx.Self:
        r"""
        Load *.inpcrd metadata from a file path

        To correctly load the metadata, it *must* be known if the structure has
        a box or not, otherwise the whole file will have to be read, and
        whether the box is present or not can only be inferred from the number
        of atoms.
        """
        path = Path(path).resolve()
        with open(path, mode="rb") as f:
            f.seek(0)
            name, atoms_num = list(itertools.islice(f, 0, 2))
            if has_box:
                f.seek(-80, os.SEEK_END)
                box = f.readlines()[-1].decode("ascii").split()
                box_params = BoxParams(
                    np.array(box[:3], dtype=np.float64),
                    np.array(box[3:], dtype=np.float64),
                )
            else:
                box_params = None
        return cls(
            name.decode("ascii"),
            int(atoms_num.decode("ascii")),
            box_params,
        )


@dataclass
class Inpcrd:
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
    def box_lengths(self) -> NDArray[np.float64]:
        if self.box_params is None:
            raise ValueError("There should be box parameters to get box lengths")
        return self.box_params.lengths

    @property
    def box_angles(self) -> NDArray[np.float64]:
        if self.box_params is None:
            raise ValueError("There should be box parameters to get box angles")
        return self.box_params.angles

    @property
    def has_box(self) -> bool:
        return self.box_params is not None

    @classmethod
    def load(
        cls,
        path: Path,
    ) -> tpx.Self:
        # import here to improve startup time
        import pandas  # noqa

        path = Path(path).resolve()
        name, atoms_num = _read_name_and_num_atoms(path)
        df = pandas.read_csv(path, skiprows=2, sep=r"\s+", header=None)
        floats = df.values.reshape(-1, 3)
        coordinates = floats[:atoms_num]
        box = floats[atoms_num:]

        box_params: tp.Optional[BoxParams]
        if box.shape[0] == 0 or np.isnan(box).all():
            box_params = None
        else:
            box_params = BoxParams(box[-2, :], box[-1, :])
        return cls(
            name=name,
            coordinates=coordinates,
            box_params=box_params,
        )

    def dump(self, path: Path) -> None:

        with open(path, mode="w+", encoding="utf-8") as f:
            f.write(f"{self.name}\n")
            f.write(f"{self.atoms_num:6d}\n")
            num_coords = self.coordinates.shape[0] * 3

            if ((num_coords // 6) * 6) != num_coords:
                final_row = self.coordinates[-1]
                reshaped = self.coordinates[:-1].reshape(-1, 6)
            else:
                final_row = np.array([], dtype=np.float32)
                reshaped = self.coordinates.reshape(-1, 6)
            for row in reshaped:
                f.write("".join((f"{el:12.7f}" for el in row)))
                f.write("\n")
            if final_row.size > 0:
                f.write("".join((f"{el:12.7f}" for el in final_row)))
                f.write("\n")
            if self.box_params is not None:
                lengths = self.box_params.lengths
                angles = self.box_params.angles
                f.write(
                    "".join((f"{el:12.7f}" for el in np.concatenate((lengths, angles))))
                )
                f.write("\n")


def _read_name_and_num_atoms(path: Path) -> tp.Tuple[str, int]:
    with open(path, mode="r", encoding="utf-8") as f:
        for j, line in enumerate(f):
            if j == 0:
                name = line.strip()
            elif j == 1:
                atoms_num = int(line.strip())
            else:
                break
    return name, atoms_num
