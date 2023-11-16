from enum import Enum
from dataclasses import dataclass


class Plane(Enum):
    YZ = 1
    XZ = 2
    XY = 3


@dataclass
class SurfaceTensionstat:
    tension_dyne_per_cm: float
    plane: Plane
    interface_num: int = 2


@dataclass
class AmberSurfaceTensionstat(SurfaceTensionstat):
    # Not sure what this tensionstat does ?
    pass
