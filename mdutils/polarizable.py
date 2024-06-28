from enum import Enum

import typing_extensions as tpx

_PRMTOP_IDX_MAP = {
    "no-polarizable": 0,
    "polarizable": 1,
    "polarizable-with-dipole-damp": 2,
}


class PolarizableKind(Enum):
    NONE = "no-polarizable"
    POLARIZABILITY = "polarizable"
    POLARIZABILITY_AND_DIPOLE_DAMP_FACTOR = "polarizable-with-dipole-damp"

    @property
    def prmtop_idx(self) -> int:
        return _PRMTOP_IDX_MAP[self.value]

    @classmethod
    def from_prmtop_idx(cls, idx: int) -> tpx.Self:
        value = {v: k for k, v in _PRMTOP_IDX_MAP.items()}[idx]
        return cls(value)
