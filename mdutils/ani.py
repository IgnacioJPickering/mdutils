from enum import Enum


class AniModelKind(Enum):
    ANI1X = "ani1x"
    ANI1CCX = "ani1ccx"
    ANI2X = "ani2x"
    ANIMBIS = "animbis"
    ANIALA = "aniala"
    ANIDR = "anidr"


class AniNeighborlistKind(Enum):
    AUTO = "auto"
    EXTERNAL = "external"
    INTERNAL_CELL_LIST = "internal-cell-list"
    INTERNAL_ALL_PAIRS = "internal-all-pairs"
