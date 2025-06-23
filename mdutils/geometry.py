import typing as tp
import math
from enum import Enum
from dataclasses import dataclass, field

import numpy as np
from numpy.typing import NDArray
import typing_extensions as tpx


class CoordKind(Enum):
    BOND = "B"
    ANGLE = "A"
    DIHEDRAL = "D"


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


# These functions calculate bond distances, bond angles and dihedrals in batch
def bond_dist(a: NDArray[np.float64], b: NDArray[np.float64]) -> NDArray[np.float64]:
    r"""bond distance between atoms a, b. Accepts batched inputs"""
    a = np.atleast_2d(a)
    b = np.atleast_2d(b)
    return np.linalg.norm(b - a, axis=1)


def _angle(
    vec_a: NDArray[np.float64],
    vec_b: NDArray[np.float64],
    deg: bool = True,
) -> NDArray[np.float64]:
    norm_a = np.linalg.norm(vec_a, axis=1)
    norm_b = np.linalg.norm(vec_b, axis=1)
    retval = np.arccos(np.sum(vec_a * vec_b, axis=1) / norm_a / norm_b)
    if deg:
        retval *= 180 / math.pi
    return retval


def bond_angle(
    a: NDArray[np.float64], b: NDArray[np.float64], c: NDArray[np.float64]
) -> NDArray[np.float64]:
    r"""bond angle between atoms a, b, c in degrees. Accepts batched inputs"""
    a = np.atleast_2d(a)
    b = np.atleast_2d(b)
    c = np.atleast_2d(c)
    ba = a - b
    bc = c - b
    return _angle(ba, bc)


def dih_angle(
    a: NDArray[np.float64],
    b: NDArray[np.float64],
    c: NDArray[np.float64],
    d: NDArray[np.float64],
) -> NDArray[np.float64]:
    r"""bond angle between atoms a, b, c, d in degrees. Accepts batched inputs"""
    a = np.atleast_2d(a)
    b = np.atleast_2d(b)
    c = np.atleast_2d(c)
    d = np.atleast_2d(d)
    ab = b - a
    bc = c - b
    cd = d - c
    norml_abc = np.cross(ab, bc).astype(np.float64)
    norml_bcd = np.cross(bc, cd).astype(np.float64)
    return _angle(norml_abc, norml_bcd)


def measure(
    coords: NDArray[np.float64],
    idxs: tp.Sequence[int],
    kind: tp.Optional[tp.Union[CoordKind, str]] = None,
) -> NDArray[np.float64]:
    r"""Measure an internal coord

    This function fails gracefully with a ValueError if the number of idxs passed is
    inconsistent with the coord requested, if 'kind' is passed.
    """
    if isinstance(kind, str):
        kind = CoordKind(kind)
    if kind is None:
        if len(idxs) == 2:
            kind = CoordKind.BOND
        elif len(idxs) == 3:
            kind = CoordKind.ANGLE
        elif len(idxs) == 4:
            kind = CoordKind.DIHEDRAL
        else:
            raise ValueError("idxs must be 2, 3 or 4")
    if coords.ndim == 2:
        coords = np.expand_dims(coords, axis=0)
    if kind is CoordKind.BOND:
        if len(idxs) != 2:
            raise ValueError("Two indices expected to measure bonds")
        coords = coords[:, idxs, :]
        val = bond_dist(coords[:, 0, :], coords[:, 1, :])
    elif kind is CoordKind.ANGLE:
        if len(idxs) != 3:
            raise ValueError("Three indices expected to measure bond-angles")
        coords = coords[:, idxs, :]
        val = bond_angle(coords[:, 0, :], coords[:, 1, :], coords[:, 2, :])
    elif kind is CoordKind.DIHEDRAL:
        if len(idxs) != 4:
            raise ValueError("Four indices expected to measure dihedral-angles")
        coords = coords[:, idxs, :]
        val = dih_angle(
            coords[:, 0, :], coords[:, 1, :], coords[:, 2, :], coords[:, 3, :]
        )
    return val
