import typing as tp
from dataclasses import dataclass

import numpy as np
from numpy.typing import NDArray

from mdutils.yaml import yamlize, YamlEnum


@dataclass
class BoxParams:
    lengths: NDArray[np.float_]
    _angles: tp.Tuple[float, float, float] = (90.0, 90.0, 90.0)

    @property
    def angles(self) -> NDArray[np.float_]:
        return np.array(self._angles)


@yamlize
class BoxKind(YamlEnum):
    NO_BOX = 0
    RECTANGULAR = 1  # Should be PARALLELEPIPED
    TRUNCATED_OCTAHEDRAL = 2
    RECTANGULAR_CUBOID = 3  # all angles are 90 deg
