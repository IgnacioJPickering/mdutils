from enum import Enum


class InitialVelocities(Enum):
    MAXWELL_BOLTZMANN = "maxwell-boltzmann"
    FROM_STRUCTURE = "vel-from-structure"
    ZERO = "zero-vel"
