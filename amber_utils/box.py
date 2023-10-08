from dataclasses import dataclass
from enum import Enum

import numpy as np
from numpy.typing import NDArray


@dataclass
class BoxParams:
    lengths: NDArray[np.float_]
    angles: NDArray[np.float_]


class BoxKind(Enum):
    NO_BOX = 0
    RECTANGULAR = 1
    TRUNCATED_OCTAHEDRAL = 2
