from enum import Enum

AMBER_ANI_INTERFACE_MAP = {
    "1x": "ani1x",
    "2x": "ani2x",
    "1ccx": "ani1ccx",
    "mbis2x": "animbis",
    "dr": "anidr",
    "2dr": "ani2dr",
    "2xr": "ani2xr",
    "ala": "aniala",
}


class AniNeighborlistKind(Enum):
    AUTO = "auto"
    EXTERNAL = "external"
    INTERNAL_CELL_LIST = "internal-cell-list"
    INTERNAL_ALL_PAIRS = "internal-all-pairs"
