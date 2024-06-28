from enum import Enum

AMBER_ANI_INTERFACE_MAP = {
    "1x": "ani1x",
    "2x": "ani2x",
    "1ccx": "ani1ccx",
    "mbis2x": "animbis",
    "dr": "anidr",
    "ala": "aniala",
}


class ModelKind(Enum):
    ANI1X = "1x"
    ANI1CCX = "1ccx"
    ANI2X = "2x"
    ANI2XQ = "mbis2x"
    ANIALA = "ala"
    ANIDR = "dr"
    FF = "ff"  # Use whatever ff parameters are defined in the prmtop file


class AniNeighborlistKind(Enum):
    AUTO = "auto"
    EXTERNAL = "external"
    INTERNAL_CELL_LIST = "internal-cell-list"
    INTERNAL_ALL_PAIRS = "internal-all-pairs"


ANI_MODELS = {
    ModelKind.ANIDR,
    ModelKind.ANIALA,
    ModelKind.ANI1X,
    ModelKind.ANI2X,
    ModelKind.ANI1CCX,
    ModelKind.ANI2XQ,
}
