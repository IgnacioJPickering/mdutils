from enum import Enum

AMBER_ANI_INTERFACE_MAP = {
    "ANI1x": "ani1x",
    "ANI2x": "ani2x",
    "ANI1ccx": "ani1ccx",
    "ANI2xCharges": "animbis",
}


class AniNeighborlistKind(Enum):
    AUTO = "auto"
    EXTERNAL = "external"
    INTERNAL_CELL_LIST = "internal-cell-list"
    INTERNAL_ALL_PAIRS = "internal-all-pairs"
