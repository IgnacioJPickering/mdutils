import typing_extensions as tpx
from pathlib import Path
import dataclasses

from mdutils.amber.mdcrd import Mdcrd
from mdutils.amber.prmtop import Prmtop


@dataclasses.dataclass
class AmberTraj:
    r"""Manage amber "trajectories", consisting of an mdcrd and a prmtop file"""

    prmtop: Prmtop
    mdcrd: Mdcrd

    @classmethod
    def load(cls, prmtop_path: Path, mdcrd_path: Path) -> tpx.Self:
        prmtop = Prmtop.load(prmtop_path)
        mdcrd = Mdcrd.load(mdcrd_path)
        return cls(prmtop, mdcrd)
