from enum import Enum


class Optimizer(Enum):
    DEFAULT = "default"
    LBFGS = "lbfgs"
    BFGS = "bfgs"
    FIRE = "fire"
    STEEPEST_DESCENT = "steepest-descent"
