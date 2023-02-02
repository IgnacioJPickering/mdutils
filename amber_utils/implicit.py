from enum import Enum
from typing import Optional


# The first tuple element is the name of the "set default PBRadii" command
# in leap, the second is the igb value in amber
# they can be accessed with radii_name and mdin_int


class ImplicitSolventModel(Enum):
    GB = ("mbondi", 1)
    MODIFIED_GB_I = ("mbondi2", 2)
    MODIFIED_GB_II = ("mbondi2", 5)
    GBN = ("bondi", 5)
    MODIFIED_GBN = ("bondi", 7)
    POISSON_BOLTZMANN = (None, 10)
    VACUUM = (None, 6)

    def __init__(self, radii_name: Optional[str], mdin_int: int):
        self.radii_name = radii_name
        self.mdin_int = mdin_int

    @property
    def leap_command(self) -> str:
        # get the command necessary to set the appropriate radii
        # in leap
        if self.radii_name is not None:
            return f"set default PBRadii {self.radii_name}"
        return ""
