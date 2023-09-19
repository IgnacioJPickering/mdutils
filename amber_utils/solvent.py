from enum import Enum


class SolventModel(Enum):
    EXPLICIT = "explicit"
    GB = "GB"
    MODIFIED_GB_I = "modified-GB-I"
    MODIFIED_GB_II = "modified-GB-II"
    GBN = "GBn"
    MODIFIED_GBN = "modified-GBn"
    POISSON_BOLTZMANN = "PB"
    VACUUM = "vacuum"


_MDIN_MAP = {
    SolventModel.GB: 1,
    SolventModel.MODIFIED_GB_I: 2,
    SolventModel.MODIFIED_GB_II: 5,
    SolventModel.GBN: 7,
    SolventModel.MODIFIED_GBN: 8,
    SolventModel.POISSON_BOLTZMANN: 10,
    SolventModel.VACUUM: 6,
}


def mdin_integer(model: SolventModel) -> int:
    return _MDIN_MAP[model]
