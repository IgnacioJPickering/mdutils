r"""
Utilities to deal with Amber-style netCDF 'restart' files
"""

import typing_extensions as tpx
from dataclasses import dataclass
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
        ncds = netcdf.Dataset(str(path), "r", format="NETCDF3_64BIT_OFFSET")
        box_params: tp.Optional[BoxParams]
        try:
            box_params = BoxParams(
                ncds["cell_lengths"][:].data,
                ncds["cell_angles"][:].data,
            )
        except IndexError:
            box_params = None
        return cls(
            name=getattr(ncds, "title", ""),
            time_ps=ncds["time"][:].data.item(),
            program=getattr(ncds, "program", ""),
            application=getattr(ncds, "application", ""),
            program_version=getattr(ncds, "programVersion", ""),
            box_params=box_params,
        )


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
    coordinates: NDArray[np.float32]
    time_ps: float = 0.0
    velocities: tp.Optional[NDArray[np.float32]] = None
    forces: tp.Optional[NDArray[np.float32]] = None
    box_params: tp.Optional[BoxParams] = None
    application: str = ""
    program: str = ""
    program_version: str = ""

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
        dataset = netcdf.Dataset(str(path), "w", format="NETCDF3_64BIT_OFFSET")

        # Global Attributes
        dataset.Conventions = "AMBERRESTART"
        dataset.ConventionVersion = "1.0"
        dataset.program = self.program
        dataset.programVersion = self.program_version

        # Optional Global Attributes
        dataset.application = self.application
        dataset.title = self.name
        dataset.createDimension("atom", self.atoms_num)
        dataset.createDimension("spatial", 3)

        spatial_label = dataset.createVariable("spatial", "c", ("spatial",))
        spatial_label[:] = "xyz"
        coordinates_var = dataset.createVariable(
            "coordinates", "f8", ("atom", "spatial")
        )
        coordinates_var.units = "angstrom"
        dataset["coordinates"][:] = self.coordinates
        time_var = dataset.createVariable("time", "f8")
        time_var.units = "picosecond"
        dataset["time"][:] = np.array(self.time_ps, dtype=np.float64)

        velocities = self.velocities
        if velocities is not None:
            velocities_var = dataset.createVariable(
                "velocities", "f8", ("atom", "spatial")
            )
            velocities_var.units = "angstrom/picosecond"
            # In order for velocities to actually be in angstrom / picosecond, they
            # must be multiplied by the scale factor
            velocities_var.scale_factor = AMBER_VELOCITIES_SCALE_FACTOR
            dataset["velocities"][:] = velocities
        forces = self.forces
        if forces is not None:
            forces_var = dataset.createVariable("forces", "f8", ("atom", "spatial"))
            forces_var.units = "kilocalorie/mole/angstrom"
            dataset["forces"][:] = forces

        if self.has_box:
            dataset.createDimension("cell_spatial", 3)
            dataset.createDimension("cell_angular", 3)
            dataset.createDimension("label", 5)
            cell_spatial_label = dataset.createVariable(
                "cell_spatial", "c", ("cell_spatial",)
            )
            cell_spatial_label[:] = "abc"

            cell_angular_label = dataset.createVariable(
                "cell_angular", "c", ("cell_angular", "label")
            )
            cell_angular_label[0, :] = "alpha"
            cell_angular_label[1, :] = "beta "
            cell_angular_label[2, :] = "gamma"
            cell_lengths_var = dataset.createVariable(
                "cell_lengths",
                "f8",
                ("cell_spatial",),
            )
            cell_angles_var = dataset.createVariable(
                "cell_angles",
                "f8",
                ("cell_angular",),
            )
            cell_lengths_var.units = "angstrom"
            cell_angles_var.units = "degree"
            dataset["cell_lengths"][:] = self.box_lengths
            dataset["cell_angles"][:] = self.box_angles

    @classmethod
    def load(cls, path: Path) -> tpx.Self:
        meta = RestartMeta.load(path)
        netcdf_ds = netcdf.Dataset(str(path), "r", format="NETCDF3_64BIT_OFFSET")
        coordinates = netcdf_ds["coordinates"][:].data
        try:
            velocities = netcdf_ds["velocities"][:].data * AMBER_VELOCITIES_SCALE_FACTOR
        except IndexError:
            velocities = None
        try:
            forces = netcdf_ds["forces"][:].data
        except IndexError:
            forces = None
        return cls(
            forces=forces,
            coordinates=coordinates,
            velocities=velocities,
            name=meta.name,
            program=meta.program,
            program_version=meta.program_version,
            application=meta.application,
            time_ps=meta.time_ps,
            box_params=meta.box_params,
        )
