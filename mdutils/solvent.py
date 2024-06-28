from enum import Enum


class SolventModel(Enum):
    EXPLICIT = "explicit"
    GB = "gb"
    MODIFIED_GB_I = "gb-mod1"
    MODIFIED_GB_II = "gb-mod2"
    GBN = "gbn"
    MODIFIED_GBN = "gbn-mod"
    POISSON_BOLTZMANN = "pb"
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
