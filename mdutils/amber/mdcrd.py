r"""
Utilities to deal with Amber-style netCDF 'mdcrd' files
"""

import typing_extensions as tpx
from dataclasses import dataclass, field
import typing as tp
from pathlib import Path

import numpy as np
import netCDF4 as netcdf
from numpy.typing import NDArray

from mdutils.units import AMBER_VELOCITIES_SCALE_FACTOR
from mdutils.geometry import (
    BoxParamsTraj,
    bond_dist,
    bond_angle,
    dih_angle,
    measure,
    CoordKind,
)

__all__ = ["Mdcrd", "MdcrdMeta"]


@dataclass
class MdcrdMeta:
    name: str
    application: str = ""
    program: str = ""
    program_version: str = ""
    has_box: bool = False
    has_velocities: bool = False
    has_forces: bool = False
    atoms_num: tp.Optional[int] = None
    steps_num: tp.Optional[int] = None

    @classmethod
    def load(cls, path: Path) -> tpx.Self:
        netcdf_ds = netcdf.Dataset(str(path), "r", format="NETCDF3_64BIT_OFFSET")
        steps_num, atoms_num, _ = netcdf_ds["coordinates"].shape
        try:
            _ = netcdf_ds["cell_lengths"]
            has_box = True
        except IndexError:
            has_box = False
        try:
            _ = netcdf_ds["velocities"]
            has_velocities = True
        except IndexError:
            has_velocities = False
        try:
            _ = netcdf_ds["forces"]
            has_forces = True
        except IndexError:
            has_forces = False
        obj = cls(
            name=getattr(netcdf_ds, "title", ""),
            program=getattr(netcdf_ds, "program", ""),
            application=getattr(netcdf_ds, "application", ""),
            program_version=getattr(netcdf_ds, "programVersion", ""),
            has_box=has_box,
            has_forces=has_forces,
            has_velocities=has_velocities,
            atoms_num=atoms_num,
            steps_num=steps_num,
        )
        netcdf_ds.close()
        return obj


@dataclass
class Mdcrd:
    r"""
    Manage data inside Amber *.mdcrd 'trajectory' netCDF files
    """

    name: str
    time_ps: NDArray[np.float32]
    coordinates: NDArray[np.float32]
    forces: tp.Optional[NDArray[np.float32]] = None
    box_params_traj: tp.Optional[BoxParamsTraj] = None
    application: str = ""
    program: str = ""
    program_version: str = ""

    # Internal field
    velocities_amber_units: tp.Optional[NDArray[np.float32]] = field(
        default=None, init=False
    )

    @property
    def atoms_num(self) -> int:
        return self.coordinates.shape[1]

    @property
    def velocities(self) -> tp.Optional[NDArray[np.float32]]:
        # Outputs velocities in ang/ps
        if self.velocities_amber_units is None:
            return None
        return self.velocities_amber_units * AMBER_VELOCITIES_SCALE_FACTOR

    @velocities.setter
    def velocities(self, value: tp.Optional[NDArray[np.float32]]) -> None:
        if value is None:
            self.velocities_amber_units = None
        else:
            self.velocities_amber_units = value / AMBER_VELOCITIES_SCALE_FACTOR

    @property
    def has_velocities(self) -> bool:
        return self.velocities is not None

    @property
    def has_forces(self) -> bool:
        return self.forces is not None

    @property
    def has_box(self) -> bool:
        return self.box_params_traj is not None

    @property
    def box_lengths(self) -> NDArray[np.float32]:
        if self.box_params_traj is None:
            raise ValueError("There should be box parameters to get box lengths")
        return self.box_params_traj.lengths

    @property
    def box_angles(self) -> NDArray[np.float32]:
        if self.box_params_traj is None:
            raise ValueError("There should be box parameters to get box angles")
        return self.box_params_traj.angles

    def dump(
        self,
        path: Path,
    ) -> None:
        netcdf_ds = netcdf.Dataset(str(path), "w", format="NETCDF3_64BIT_OFFSET")

        # Global Attributes
        netcdf_ds.Conventions = "AMBER"
        netcdf_ds.ConventionVersion = "1.0"
        netcdf_ds.program = self.program
        netcdf_ds.programVersion = self.program_version

        # Optional Global Attributes
        netcdf_ds.application = self.application
        netcdf_ds.title = self.name
        netcdf_ds.createDimension("atom", self.atoms_num)
        netcdf_ds.createDimension("spatial", 3)
        netcdf_ds.createDimension("frame", None)

        spatial_label = netcdf_ds.createVariable("spatial", "c", ("spatial",))
        spatial_label[:] = "xyz"
        coordinates_var = netcdf_ds.createVariable(
            "coordinates", "f4", ("frame", "atom", "spatial")
        )
        coordinates_var.units = "angstrom"
        netcdf_ds["coordinates"][:] = self.coordinates
        time_var = netcdf_ds.createVariable("time", "f4", ("frame",))
        time_var.units = "picosecond"
        netcdf_ds["time"][:] = np.array(self.time_ps, dtype=np.float64)

        if self.has_velocities:
            velocities_var = netcdf_ds.createVariable(
                "velocities", "f4", ("atom", "spatial")
            )
            velocities_var.units = "angstrom/picosecond"
            # In order for velocities to actually be in angstrom / picosecond, they
            # must be multiplied by the scale factor
            velocities_var.scale_factor = AMBER_VELOCITIES_SCALE_FACTOR
            netcdf_ds["velocities"][:] = self.velocities_amber_units

        if self.has_forces:
            forces_var = netcdf_ds.createVariable("forces", "f4", ("atom", "spatial"))
            forces_var.units = "kilocalorie/mole/angstrom"
            netcdf_ds["forces"][:] = self.forces

        if self.has_box:
            netcdf_ds.createDimension("cell_spatial", 3)
            netcdf_ds.createDimension("cell_angular", 3)
            netcdf_ds.createDimension("label", 5)
            cell_spatial_label = netcdf_ds.createVariable(
                "cell_spatial", "c", ("cell_spatial",)
            )
            cell_spatial_label[:] = "abc"

            cell_angular_label = netcdf_ds.createVariable(
                "cell_angular", "c", ("cell_angular", "label")
            )
            cell_angular_label[0, :] = "alpha"
            cell_angular_label[1, :] = "beta "
            cell_angular_label[2, :] = "gamma"
            cell_lengths_var = netcdf_ds.createVariable(
                "cell_lengths",
                "f4",
                (
                    "frame",
                    "cell_spatial",
                ),
            )
            cell_angles_var = netcdf_ds.createVariable(
                "cell_angles",
                "f4",
                (
                    "frame",
                    "cell_angular",
                ),
            )
            cell_lengths_var.units = "angstrom"
            cell_angles_var.units = "degree"
            netcdf_ds["cell_lengths"][:] = self.box_lengths
            netcdf_ds["cell_angles"][:] = self.box_angles
        netcdf_ds.close()

    @classmethod
    def load(cls, path: Path) -> tpx.Self:
        meta = MdcrdMeta.load(path)
        netcdf_ds = netcdf.Dataset(str(path), "r", format="NETCDF3_64BIT_OFFSET")
        coordinates = netcdf_ds["coordinates"][:].data
        time_ps = netcdf_ds["time"][:].data
        try:
            vel_amber_units = netcdf_ds["velocities"][:].data
        except IndexError:
            vel_amber_units = None
        try:
            forces = netcdf_ds["forces"][:].data
        except IndexError:
            forces = None
        try:
            box_lengths = netcdf_ds["cell_lengths"][:].data
            box_angles = netcdf_ds["cell_angles"][:].data
            box_params_traj = BoxParamsTraj(box_lengths, box_angles)
        except IndexError:
            box_params_traj = None
        netcdf_ds.close()
        obj = cls(
            forces=forces,
            time_ps=time_ps,
            coordinates=coordinates,
            name=meta.name,
            program=meta.program,
            program_version=meta.program_version,
            application=meta.application,
            box_params_traj=box_params_traj,
        )
        obj.velocities_amber_units = vel_amber_units
        return obj

    # TODO: Fix unnecessary casts to float64
    # Simple geometric calculation utilities
    def distance(self, idx0: int, idx1: int) -> NDArray[np.float64]:
        atom0 = self.coordinates[:, idx0]
        atom1 = self.coordinates[:, idx1]
        return bond_dist(atom0.astype(np.float64), atom1.astype(np.float64))

    def angle(self, idx0: int, idx1: int, idx2: int) -> NDArray[np.float64]:
        atom0 = self.coordinates[:, idx0]
        atom1 = self.coordinates[:, idx1]
        atom2 = self.coordinates[:, idx2]
        return bond_angle(
            atom0.astype(np.float64), atom1.astype(np.float64), atom2.astype(np.float64)
        )

    def dihedral(
        self, idx0: int, idx1: int, idx2: int, idx3: int
    ) -> NDArray[np.float64]:
        atom0 = self.coordinates[:, idx0]
        atom1 = self.coordinates[:, idx1]
        atom2 = self.coordinates[:, idx2]
        atom3 = self.coordinates[:, idx3]
        return dih_angle(
            atom0.astype(np.float64),
            atom1.astype(np.float64),
            atom2.astype(np.float64),
            atom3.astype(np.float64),
        )

    def measure(
        self,
        idxs: tp.Sequence[int],
        kind: tp.Optional[tp.Union[CoordKind, str]] = None,
    ) -> NDArray[np.float64]:
        return measure(self.coordinates.astype(np.float64), idxs, kind)
