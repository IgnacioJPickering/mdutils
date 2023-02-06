from enum import Enum
from typing import Optional


# The first tuple element is the name of the "set default PBRadii" command
# in leap, the second is the igb value in amber
# they can be accessed with radii_name and mdin_int

class ImplicitSolventModel(Enum):
    GB = "GB"
    MODIFIED_GB_I = "modified-GB-I"
    MODIFIED_GB_II = "modified-GB-II"
    GBN = "GBn"
    POISSON_BOLTZMANN = "PB"
    VACUUM = "vacuum"


_MDIN_MAP = {
    ImplicitSolventModel.GB: 1,
    ImplicitSolventModel.MODIFIED_GB_I: 2,
    ImplicitSolventModel.MODIFIED_GB_II: 5,
    ImplicitSolventModel.GBN: 5,
    ImplicitSolventModel.MODIFIED_GBN: 7,
    ImplicitSolventModel.POISSON_BOLTZMANN: 10,
    ImplicitSolventModel.VACUUM: 6,
}


def mdin_integer(model: ImplicitSolventModel) -> int:
    return _MDIN_MAP[model]
