from mdutils.yaml import yamlize, YamlEnum


@yamlize
class InitialVelocities(YamlEnum):
    MAXWELL_BOLTZMANN = "maxwell-boltzmann"
    FROM_STRUCTURE = "from-structure"
    ZERO = "zero"
