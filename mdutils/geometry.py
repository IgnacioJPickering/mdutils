import typing as tp
from enum import Enum
from dataclasses import dataclass, field

import numpy as np
from numpy.typing import NDArray
import typing_extensions as tpx


# Useful for ANI models
class NeighborlistKind(Enum):
    AUTO = "auto"
    EXTERNAL = "external"
    INTERNAL_CELL_LIST = "internal-cell-list"
    INTERNAL_ALL_PAIRS = "internal-all-pairs"


class Scaling(Enum):
    ISOTROPIC = "isotropic"
    ANISOTROPIC_RANDOM = "anisotropic-random"
    ANISOTROPIC_X = "anisotropic-x"
    ANISOTROPIC_Y = "anisotropic-y"
    ANISOTROPIC_Z = "anisotropic-z"


_PRMTOP_IDX_MAP = {
    "yz-plane": 1,
    "xz-plane": 2,
    "xy-plane": 3,
}


class Plane(Enum):
    YZ = "yz-plane"
    XZ = "xz-plane"
    XY = "xy-plane"

    @property
    def prmtop_idx(self) -> int:
        return _PRMTOP_IDX_MAP[self.value]

    @classmethod
    def from_prmtop_idx(cls, idx: int) -> tpx.Self:
        value = {v: k for k, v in _PRMTOP_IDX_MAP.items()}[idx]
        return cls(value)


@dataclass
class BoxParams:
    lengths: NDArray[np.float64] = field(
        default_factory=lambda: np.full(3, fill_value=1.0, dtype=np.float64)
    )
    angles: NDArray[np.float64] = field(
        default_factory=lambda: np.full(3, fill_value=90.0, dtype=np.float64)
    )


class SolvCapKind(Enum):
    NO_SOLV_CAP = "no-solv-cap"
    SPHERE = "sphere"

    @property
    def prmtop_idx(self) -> int:
        return self._prmtop_idx_map()[self.value]

    @classmethod
    def from_prmtop_idx(cls, idx: int) -> tpx.Self:
        value = {v: k for k, v in cls._prmtop_idx_map().items()}[idx]
        return cls(value)

    @staticmethod
    def _prmtop_idx_map() -> tp.Dict[str, int]:
        return {
            "no-solv-cap": 0,
            "sphere": 1,
        }


class BoxKind(Enum):
    NO_BOX = "no-box"
    RECTANGULAR_CUBOID = "rect-cuboid"  # All angles are 90 deg
    PARALLELEPIPED = "parallelepiped"  # Angles can be whatever
    TRUNCATED_OCTAHEDRON = "truc-octahedron"

    @property
    def prmtop_idx(self) -> int:
        return self._prmtop_idx_map()[self.value]

    @classmethod
    def from_prmtop_idx(cls, idx: int) -> tpx.Self:
        value = {v: k for k, v in cls._prmtop_idx_map().items()}[idx]
        return cls(value)

    @staticmethod
    def _prmtop_idx_map() -> tp.Dict[str, int]:
        return {
            "no-box": 0,
            "parallelepiped": 1,
            "trunc-octahedron": 2,
            "rect-cuboid": 3,
        }
