from enum import Enum
import typing as tp
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray
import typing_extensions as tpx


@dataclass
class BoxParams:
    _lengths: tp.Tuple[float, float, float] = (1.0, 1.0, 1.0)
    _angles: tp.Tuple[float, float, float] = (90.0, 90.0, 90.0)

    @property
    def angles(self) -> NDArray[np.float_]:
        return np.array(self._angles)

    @property
    def lengths(self) -> NDArray[np.float_]:
        return np.array(self._lengths)


_PRMTOP_IDX_MAP = {
    "no-box": 0,
    "parallelepiped": 1,
    "trunc-octahedron": 2,
    "rect-cuboid": 3,
}


class BoxKind(Enum):
    NO_BOX = "no-box"
    RECTANGULAR_CUBOID = "rect-cuboid"  # All angles are 90 deg
    PARALLELEPIPED = "parallelepiped"  # Angles can be whatever
    TRUNCATED_OCTAHEDRON = "truc-octahedron"

    @property
    def prmtop_idx(self) -> int:
        return _PRMTOP_IDX_MAP[self.value]

    @classmethod
    def from_prmtop_idx(cls, idx: int) -> tpx.Self:
        value = {v: k for k, v in _PRMTOP_IDX_MAP.items()}[idx]
        return cls(value)
