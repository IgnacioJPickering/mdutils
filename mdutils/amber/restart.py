r"""
Utilities to deal with Amber-style netCDF 'restart' files
"""

import typing_extensions as tpx
from dataclasses import dataclass, field
import typing as tp
from pathlib import Path

import numpy as np
import netCDF4 as netcdf
from numpy.typing import NDArray

from mdutils.units import AMBER_VELOCITIES_SCALE_FACTOR
from mdutils.geometry import BoxParams

from mdutils.amber.input_system import _BaseInputSystem

__all__ = ["Restart", "RestartMeta"]


@dataclass
class RestartMeta:
    name: str
    time_ps: float = 0.0
    application: str = ""
    program: str = ""
    program_version: str = ""
    box_params: tp.Optional[BoxParams] = None

    @classmethod
    def load(cls, path: Path) -> tpx.Self:
        netcdf_ds = netcdf.Dataset(str(path), "r", format="NETCDF3_64BIT_OFFSET")
        box_params: tp.Optional[BoxParams]
        try:
            box_params = BoxParams(
                netcdf_ds["cell_lengths"][:].data,
                netcdf_ds["cell_angles"][:].data,
            )
        except IndexError:
            box_params = None
        obj = cls(
            name=getattr(netcdf_ds, "title", ""),
            time_ps=netcdf_ds["time"][:].data.item(),
            program=getattr(netcdf_ds, "program", ""),
            application=getattr(netcdf_ds, "application", ""),
            program_version=getattr(netcdf_ds, "programVersion", ""),
            box_params=box_params,
        )
        netcdf_ds.close()
        return obj


@dataclass
class Restart(_BaseInputSystem):
    r"""
    Manage data inside Amber *.restrt 'restart' netCDF files

    Restart files can be used as initial values for simulations, or to restart
    suspended simulations.

    Data in the files always includes coordinates, and it can optionally have
    velocities or forces if it is the result of dynamics.
    """

    name: str
    coordinates: NDArray[np.float64]
    time_ps: float = 0.0
    forces: tp.Optional[NDArray[np.float64]] = None
    box_params: tp.Optional[BoxParams] = None
    application: str = ""
    program: str = ""
    program_version: str = ""

    # Internal field
    velocities_amber_units: tp.Optional[NDArray[np.float64]] = field(
        default=None, init=False
    )

    @property
    def velocities(self) -> tp.Optional[NDArray[np.float64]]:
        # Outputs velocities in ang/ps
        if self.velocities_amber_units is None:
            return None
        return self.velocities_amber_units * AMBER_VELOCITIES_SCALE_FACTOR

    @velocities.setter
    def velocities(self, value: tp.Optional[NDArray[np.float64]]) -> None:
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

    def dump(
        self,
        path: Path,
    ) -> None:
        netcdf_ds = netcdf.Dataset(str(path), "w", format="NETCDF3_64BIT_OFFSET")

        # Global Attributes
        netcdf_ds.Conventions = "AMBERRESTART"
        netcdf_ds.ConventionVersion = "1.0"
        netcdf_ds.program = self.program
        netcdf_ds.programVersion = self.program_version

        # Optional Global Attributes
        netcdf_ds.application = self.application
        netcdf_ds.title = self.name
        netcdf_ds.createDimension("atom", self.atoms_num)
        netcdf_ds.createDimension("spatial", 3)

        spatial_label = netcdf_ds.createVariable("spatial", "c", ("spatial",))
        spatial_label[:] = "xyz"
        coordinates_var = netcdf_ds.createVariable(
            "coordinates", "f8", ("atom", "spatial")
        )
        coordinates_var.units = "angstrom"
        netcdf_ds["coordinates"][:] = self.coordinates
        time_var = netcdf_ds.createVariable("time", "f8")
        time_var.units = "picosecond"
        netcdf_ds["time"][:] = np.array(self.time_ps, dtype=np.float64)

        if self.has_velocities:
            velocities_var = netcdf_ds.createVariable(
                "velocities", "f8", ("atom", "spatial")
            )
            velocities_var.units = "angstrom/picosecond"
            # In order for velocities to actually be in angstrom / picosecond, they
            # must be multiplied by the scale factor
            velocities_var.scale_factor = AMBER_VELOCITIES_SCALE_FACTOR
            netcdf_ds["velocities"][:] = self.velocities_amber_units

        if self.has_forces:
            forces_var = netcdf_ds.createVariable("forces", "f8", ("atom", "spatial"))
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
                "f8",
                ("cell_spatial",),
            )
            cell_angles_var = netcdf_ds.createVariable(
                "cell_angles",
                "f8",
                ("cell_angular",),
            )
            cell_lengths_var.units = "angstrom"
            cell_angles_var.units = "degree"
            netcdf_ds["cell_lengths"][:] = self.box_lengths
            netcdf_ds["cell_angles"][:] = self.box_angles
        netcdf_ds.close()

    @classmethod
    def load(cls, path: Path) -> tpx.Self:
        meta = RestartMeta.load(path)
        netcdf_ds = netcdf.Dataset(str(path), "r", format="NETCDF3_64BIT_OFFSET")
        coordinates = netcdf_ds["coordinates"][:].data
        try:
            vel_amber_units = netcdf_ds["velocities"][:].data
        except IndexError:
            vel_amber_units = None
        try:
            forces = netcdf_ds["forces"][:].data
        except IndexError:
            forces = None
        netcdf_ds.close()
        obj = cls(
            forces=forces,
            coordinates=coordinates,
            name=meta.name,
            program=meta.program,
            program_version=meta.program_version,
            application=meta.application,
            time_ps=meta.time_ps,
            box_params=meta.box_params,
        )
        obj.velocities_amber_units = vel_amber_units
        return obj
