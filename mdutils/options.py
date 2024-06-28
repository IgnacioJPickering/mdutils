from enum import Enum


class Step(Enum):
    MD = "md"
    MIN = "min"


class Ensemble(Enum):
    # These include minimization, heating, and prelax, what changes is the production
    NVT = "nvt"
    NPT = "npt"
    NVE = "nve"
