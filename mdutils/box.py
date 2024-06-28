from enum import Enum
import typing as tp
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray


@dataclass
class BoxParams:
    lengths: NDArray[np.float_]
    _angles: tp.Tuple[float, float, float] = (90.0, 90.0, 90.0)

    @property
    def angles(self) -> NDArray[np.float_]:
        return np.array(self._angles)


class BoxKind(Enum):
    NO_BOX = "no-box"  # 0
    PARALLELEPIPED = "parallelepiped"  # 1  # Angles can be whatever
    TRUNCATED_OCTAHEDRON = "truc-octahedron"  # 2
    RECTANGULAR_CUBOID = "rectangular-cuboid"  # 3  # All angles are 90 deg
