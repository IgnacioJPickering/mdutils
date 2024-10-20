r"""
Private input system base class
"""
import typing_extensions as tpx
from pathlib import Path
from numpy.typing import NDArray
import numpy as np
import typing as tp
from dataclasses import dataclass

from mdutils.geometry import BoxParams


@dataclass
class _BaseInputSystem:
    name: str
    coordinates: NDArray[np.float64]
    box_params: tp.Optional[BoxParams] = None

    @property
    def has_velocities(self) -> bool:
        return False

    @property
    def has_forces(self) -> bool:
        return False

    @property
    def has_box(self) -> bool:
        return self.box_params is not None

    @property
    def atoms_num(self) -> int:
        return self.coordinates.shape[0]

    @property
    def box_lengths(self) -> NDArray[np.float64]:
        if self.box_params is None:
            raise ValueError("There should be box parameters to get box lengths")
        return self.box_params.lengths

    @property
    def box_angles(self) -> NDArray[np.float64]:
        if self.box_params is None:
            raise ValueError("There should be box parameters to get box angles")
        return self.box_params.angles

    @classmethod
    def load(cls, path: Path) -> tpx.Self:
        raise NotImplementedError()

    def dump(self, path: Path) -> None:
        raise NotImplementedError()
