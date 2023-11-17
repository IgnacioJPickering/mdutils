from enum import Enum


class InitialVelocities(Enum):
    MAXWELL_BOLTZMANN = "maxwell-boltzmann"
    FROM_STRUCTURE = "from-structure"
    ZERO = "zero"
