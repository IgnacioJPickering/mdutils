from mdutils.yaml import yamlize, YamlEnum


@yamlize
class Step(YamlEnum):
    MD = "md"
    MIN = "min"


@yamlize
class Ensemble(YamlEnum):
    # These include minimization, heating, and prelax, what changes is the production
    NVT = "nvt"
    NPT = "npt"
    NVE = "nve"
