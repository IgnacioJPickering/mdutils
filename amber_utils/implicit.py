from enum import Enum


class ImplicitSolventModel(Enum):
    GB = "GB"
    MODIFIED_GB_I = "modified-GB-I"
    MODIFIED_GB_II = "modified-GB-II"
    GBN = "GBn"
    MODIFIED_GBN = "modified-GBn"
    POISSON_BOLTZMANN = "PB"
    VACUUM = "vacuum"


_MDIN_MAP = {
    ImplicitSolventModel.GB: 1,
    ImplicitSolventModel.MODIFIED_GB_I: 2,
    ImplicitSolventModel.MODIFIED_GB_II: 5,
    ImplicitSolventModel.GBN: 7,
    ImplicitSolventModel.MODIFIED_GBN: 8,
    ImplicitSolventModel.POISSON_BOLTZMANN: 10,
    ImplicitSolventModel.VACUUM: 6,
}


def mdin_integer(model: ImplicitSolventModel) -> int:
    return _MDIN_MAP[model]
