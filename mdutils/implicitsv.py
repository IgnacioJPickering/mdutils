from enum import Enum

import typing_extensions as tpx


class ImplicitModelKind(Enum):
    EXPLICIT = "explicit"
    GB = "gb"
    MODIFIED_GB_I = "gb-mod1"
    MODIFIED_GB_II = "gb-mod2"
    GBN = "gbn"
    MODIFIED_GBN = "gbn-mod"
    POISSON_BOLTZMANN = "pb"
    VACUUM = "vacuum"

    @property
    def mdin_idx(self) -> int:
        return _MDIN_IDX_MAP[self.value]

    @classmethod
    def from_mdin_idx(cls, idx: int) -> tpx.Self:
        value = {v: k for k, v in _MDIN_IDX_MAP.items()}[idx]
        return cls(value)


_MDIN_IDX_MAP = {
    "gb": 1,
    "gb-mod1": 2,
    "gb-mod2": 5,
    "gbn": 7,
    "gbn-mod": 8,
    "pb": 10,
    "vacuum": 6,
}
