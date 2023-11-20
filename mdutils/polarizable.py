from mdutils.yaml import yamlize, YamlEnum


@yamlize
class PolarizableKind(YamlEnum):
    NONE = 0
    POLARIZABILITY = 1
    POLARIZABILITY_AND_DIPOLE_DAMP_FACTOR = 2
