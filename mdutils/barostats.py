from dataclasses import dataclass
from enum import Enum
import typing as tp


class Baro(Enum):
    MC = "mc"
    BERENDSEN = "berendsen"
    # BUSSI ? C-rescale (stochastic berendsen barostat) gromacs
    # MTTK for gromacs
    # TODO: add these?
    # PARRINELLO_RAHMAN = "parrinellorahman" for ase and gromacs
    # NOSE_HOOVER = "nosehoover" for lammps and ase
    # LAMMPS does not have MC barostat


class Scaling(Enum):
    ISOTROPIC = "isotropic"
    ANISOTROPIC_RANDOM = "anisotropic-random"
    ANISOTROPIC_X = "anisotropic-x"
    ANISOTROPIC_Y = "anisotropic-y"
    ANISOTROPIC_Z = "anisotropic-z"


@dataclass
class BaseBaro:
    pressure_bar: tp.Tuple[float, float] = (1.0, 1.0)
    scaling: Scaling = Scaling.ISOTROPIC

    @property
    def name(self) -> str:
        return self.__class__.__name__.replace("Baro", "").lower()


@dataclass
class BerendsenBaro(BaseBaro):
    pressure_relax_time_ps: float = 1.0
    compressibility_inv_megabar: float = 44.6


@dataclass
class McBaro(BaseBaro):
    attempts_step_interval: int = 100
