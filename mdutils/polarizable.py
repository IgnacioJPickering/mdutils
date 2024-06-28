from enum import Enum


class PolarizableKind(Enum):
    NONE = "no-polarizable"  # 0
    POLARIZABILITY = "polarizable"  # 1
    POLARIZABILITY_AND_DIPOLE_DAMP_FACTOR = "polarizable-with-dipole-damp"  # 2
