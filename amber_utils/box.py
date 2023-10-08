import typing as tp
from dataclasses import dataclass
from enum import Enum

import numpy as np
from numpy.typing import NDArray


@dataclass
class BoxParams:
    lengths: NDArray[np.float_]
    _angles: tp.Tuple[float, float, float] = (90., 90., 90.)

    @property
    def angles(self) -> NDArray[np.float_]:
        return np.array(self._angles)


class BoxKind(Enum):
    NO_BOX = 0
    RECTANGULAR = 1
    TRUNCATED_OCTAHEDRAL = 2
