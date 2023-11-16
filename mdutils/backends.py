from enum import Enum


class Backend(Enum):
    ASE = "ase"
    SANDER = "sander"
    PMEMD = "pmemd"
    OPENMM = "openmm"
    LAMMPS = "lammps"
    GROMACS = "gromacs"
    DEFAULT = "default"  # only for cli usage
