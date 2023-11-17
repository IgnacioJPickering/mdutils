from enum import Enum


class RunBackend(Enum):
    ASE = "ase"
    SANDER = "sander"
    PMEMD = "pmemd"
    OPENMM = "openmm"
    LAMMPS = "lammps"
    GROMACS = "gromacs"
