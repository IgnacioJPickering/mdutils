from mdutils.yaml import yamlize, YamlEnum


@yamlize
class DynamicsBackend(YamlEnum):
    ASE = "ase"
    SANDER = "sander"
    PMEMD = "pmemd"
    OPENMM = "openmm"
    LAMMPS = "lammps"
    GROMACS = "gromacs"
