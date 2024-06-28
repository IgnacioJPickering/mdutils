from dataclasses import dataclass
from enum import Enum


class Plane(Enum):
    YZ = "xy-plane"  # 1
    XZ = "xz-plane"  # 2
    XY = "xy-plane"  # 3


@dataclass
class SurfaceTensionstat:
    tension_dyne_per_cm: float
    plane: Plane
    interface_num: int = 2


@dataclass
class AmberSurfaceTensionstat(SurfaceTensionstat):
    # Not sure what this tensionstat does ?
    pass
