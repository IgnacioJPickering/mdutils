from mdutils.yaml import yamlize, YamlEnum

AMBER_ANI_INTERFACE_MAP = {
    "1x": "ani1x",
    "2x": "ani2x",
    "1ccx": "ani1ccx",
    "mbis2x": "animbis",
    "dr": "anidr",
    "ala": "aniala",
}


@yamlize
class ModelKind(YamlEnum):
    ANI1X = "1x"
    ANI1CCX = "1ccx"
    ANI2X = "2x"
    ANI2XQ = "mbis2x"
    ANIALA = "ala"
    ANIDR = "dr"
    FF = "ff"  # Use whatever ff parameters are defined in the prmtop file

    @classmethod
    def from_yaml(cls, constructor, node):  # type: ignore
        if node.value == "ANI2xCharges":
            str_ = "mbis2x"
        elif node.value.startswith("ANI"):
            str_ = node.value[3:]
        elif node.value.startswith("Amber"):
            str_ = node.value[5:]
        else:
            str_ = node.value
        return cls(str_)


@yamlize
class AniNeighborlistKind(YamlEnum):
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
