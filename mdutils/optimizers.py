from mdutils.yaml import yamlize, YamlEnum


@yamlize
class Optimizer(YamlEnum):
    DEFAULT = "default"
    LBFGS = "lbfgs"
    BFGS = "bfgs"
    FIRE = "fire"
    STEEPEST_DESCENT = "steepest-descent"
