from dataclasses import dataclass
from enum import Enum

import typing_extensions as tpx

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
class SurfaceTensionstat:
    tension_dyne_per_cm: float
    plane: Plane
    interface_num: int = 2


@dataclass
class AmberSurfaceTensionstat(SurfaceTensionstat):
    # Not sure what this tensionstat does (I believe it is monte-carlo)?
    pass
