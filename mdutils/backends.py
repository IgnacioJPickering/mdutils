from mdutils.yaml import yamlize, YamlEnum


@yamlize
class RunBackend(YamlEnum):
    ASE = "ase"
    SANDER = "sander"
    PMEMD = "pmemd"
    OPENMM = "openmm"
    LAMMPS = "lammps"
    GROMACS = "gromacs"
