r"""Utilities to deal with amber-style netcdf restrt files"""
from dataclasses import dataclass
import typing as tp
from pathlib import Path

import numpy as np
import netCDF4 as netcdf
from numpy.typing import NDArray

from mdutils.units import AMBER_VELOCITIES_SCALE_FACTOR
from mdutils.geometry import BoxParams

__all__ = ["AmberRestrt", "AmberRestrtMetadata", "load", "dump", "load_metadata"]


@dataclass
class AmberRestrtMetadata:
    name: str
    time_ps: float
    application: str = ""
    program: str = ""
    program_version: str = ""
    box_params: tp.Optional[BoxParams] = None


# Data in restart files can optionally have velocities or forces if it is the
# result of an MD, if it is the result of a min it only has coordinates
@dataclass
class AmberRestrt:
    name: str
    time_ps: float
    coordinates: NDArray[np.float_]
    velocities: tp.Optional[NDArray[np.float_]] = None
    forces: tp.Optional[NDArray[np.float_]] = None
    box_params: tp.Optional[BoxParams] = None
    application: str = ""
    program: str = ""
    program_version: str = ""

    @property
    def atoms_num(self) -> int:
        return self.coordinates.shape[0]

    @property
    def box_lengths(self) -> NDArray[np.float_]:
        if self.box_params is None:
            raise ValueError("There should be box parameters to get box lengths")
        return self.box_params.lengths

    @property
    def box_angles(self) -> NDArray[np.float_]:
        if self.box_params is None:
            raise ValueError("There should be box parameters to get box angles")
        return self.box_params.angles

    @property
    def has_box(self) -> bool:
        return self.box_params is not None


def dump(
    data: AmberRestrt,
    restrt: Path,
) -> None:
    dataset = netcdf.Dataset(str(restrt), "w", format="NETCDF3_64BIT_OFFSET")

    # Global Attributes
    dataset.Conventions = "AMBERRESTART"
    dataset.ConventionVersion = "1.0"
    dataset.program = data.program
    dataset.programVersion = data.program_version

    # Optional Global Attributes
    dataset.application = data.application
    dataset.title = data.name
    dataset.createDimension("atom", data.atoms_num)
    dataset.createDimension("spatial", 3)

    spatial_label = dataset.createVariable("spatial", "c", ("spatial",))
    spatial_label[:] = "xyz"
    coordinates_var = dataset.createVariable("coordinates", "f8", ("atom", "spatial"))
    coordinates_var.units = "angstrom"
    dataset["coordinates"][:] = data.coordinates
    time_var = dataset.createVariable("time", "f8")
    time_var.units = "picosecond"
    dataset["time"][:] = np.array(data.time_ps, dtype=np.float64)

    velocities = data.velocities
    if velocities is not None:
        velocities_var = dataset.createVariable("velocities", "f8", ("atom", "spatial"))
        velocities_var.units = "angstrom/picosecond"
        # In order for velocities to actually be in angstrom / picosecond, they
        # must be multiplied by the scale factor
        velocities_var.scale_factor = AMBER_VELOCITIES_SCALE_FACTOR
        dataset["velocities"][:] = velocities
    forces = data.forces
    if forces is not None:
        forces_var = dataset.createVariable("forces", "f8", ("atom", "spatial"))
        forces_var.units = "kilocalorie/mole/angstrom"
        dataset["forces"][:] = forces

    if data.has_box:
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
        dataset["cell_lengths"][:] = data.box_lengths
        dataset["cell_angles"][:] = data.box_angles


def load_metadata(restrt: Path) -> AmberRestrtMetadata:
    dataset = netcdf.Dataset(str(restrt), "r", format="NETCDF3_64BIT_OFFSET")
    try:
        name = dataset.title
    except AttributeError:
        name = ""
    try:
        program = dataset.program
    except AttributeError:
        program = ""
    try:
        program_version = dataset.programVersion
    except AttributeError:
        program_version = ""
    try:
        application = dataset.application
    except AttributeError:
        application = ""
    box_params: tp.Optional[BoxParams]
    time_ps = dataset["time"][:].data.item()
    try:
        box_params = BoxParams(
            dataset["cell_lengths"][:].data,
            dataset["cell_angles"][:].data,
        )
    except IndexError:
        box_params = None
    return AmberRestrtMetadata(
        name=name,
        time_ps=time_ps,
        program=program,
        application=application,
        program_version=program_version,
        box_params=box_params,
    )


def load(restrt: Path) -> AmberRestrt:
    metadata = load_metadata(restrt)
    dataset = netcdf.Dataset(str(restrt), "r", format="NETCDF3_64BIT_OFFSET")
    coordinates = dataset["coordinates"][:].data
    try:
        velocities = dataset["velocities"][:].data * AMBER_VELOCITIES_SCALE_FACTOR
    except IndexError:
        velocities = None
    try:
        forces = dataset["forces"][:].data
    except IndexError:
        forces = None
    return AmberRestrt(
        forces=forces,
        coordinates=coordinates,
        velocities=velocities,
        name=metadata.name,
        program=metadata.program,
        program_version=metadata.program_version,
        application=metadata.application,
        time_ps=metadata.time_ps,
        box_params=metadata.box_params,
    )
