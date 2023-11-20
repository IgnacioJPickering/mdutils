from mdutils.yaml import yamlize, YamlEnum


@yamlize
class HMR(YamlEnum):
    NONE = "none"
    NOWAT = "nowat"
    FULL = "full"
