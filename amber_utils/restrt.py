r"""Utilities to deal with amber-style netcdf restrt files"""
from dataclasses import dataclass
import typing as tp
from pathlib import Path

import numpy as np
import netCDF4 as netcdf
from numpy.typing import NDArray

from amber_utils.units import AMBER_VELOCITIES_SCALE_FACTOR
from amber_utils.box import BoxParams


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
    _write(
        restrt=restrt,
        time_ps=data.time_ps,
        coordinates=data.coordinates,
        forces=data.forces,
        velocities=data.velocities,
        box_params=data.box_params,
        name=data.name,
        program=data.program,
        application=data.application,
        program_version=data.program_version,
    )


def _write(
    restrt: Path,
    time_ps: float,
    coordinates: NDArray[np.float_],
    forces: tp.Optional[NDArray[np.float_]] = None,
    velocities: tp.Optional[NDArray[np.float_]] = None,
    box_params: tp.Optional[BoxParams] = None,
    name: str = "restrt",
    program: str = "mdrun",
    application: str = "mdrun",
    program_version: str = "0.1",
) -> None:
    dataset = netcdf.Dataset(str(restrt), "w", format="NETCDF3_64BIT_OFFSET")

    # Global Attributes
    dataset.Conventions = "AMBERRESTART"
    dataset.ConventionVersion = "1.0"
    dataset.program = program
    dataset.programVersion = program_version

    # Optional Global Attributes
    dataset.application = application
    dataset.title = name
    dataset.createDimension("atom", len(coordinates))
    dataset.createDimension("spatial", 3)

    spatial_label = dataset.createVariable("spatial", "c", ("spatial",))
    spatial_label[:] = "xyz"
    coordinates_var = dataset.createVariable("coordinates", "f8", ("atom", "spatial"))
    coordinates_var.units = "angstrom"
    dataset["coordinates"][:] = coordinates
    time_var = dataset.createVariable("time", "f8")
    time_var.units = "picosecond"
    dataset["time"][:] = np.array(time_ps, dtype=np.float64)

    if velocities is not None:
        velocities_var = dataset.createVariable("velocities", "f8", ("atom", "spatial"))
        velocities_var.units = "angstrom/picosecond"
        # In order for velocities to actually be in angstrom / picosecond, they
        # must be multiplied by the scale factor
        velocities_var.scale_factor = AMBER_VELOCITIES_SCALE_FACTOR
        dataset["velocities"][:] = velocities

    if forces is not None:
        forces_var = dataset.createVariable("forces", "f8", ("atom", "spatial"))
        forces_var.units = "kilocalorie/mole/angstrom"
        dataset["forces"][:] = forces

    if box_params is not None:
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
        # cell_angles *MUST* be present if cell_lengths is present
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
        dataset["cell_lengths"][:] = box_params.lengths
        dataset["cell_angles"][:] = box_params.angles


def _load_metadata(restrt: Path) -> tp.Tuple[str, str, str, str]:
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
    return name, program, program_version, application


def load(restrt: Path) -> AmberRestrt:
    name, program, program_version, application = _load_metadata(restrt)

    dataset = netcdf.Dataset(str(restrt), "r", format="NETCDF3_64BIT_OFFSET")
    coordinates = dataset["coordinates"][:].data
    box_params: tp.Optional[BoxParams]
    time_ps = dataset["time"][:].data.item()
    try:
        box_params = BoxParams(
            dataset["cell_lengths"][:].data,
            dataset["cell_angles"][:].data,
        )
    except IndexError:
        box_params = None
    try:
        velocities = dataset["velocities"][:].data * AMBER_VELOCITIES_SCALE_FACTOR
    except IndexError:
        velocities = None
    try:
        forces = dataset["forces"][:].data
    except IndexError:
        forces = None
    return AmberRestrt(
        name=name,
        program=program,
        program_version=program_version,
        application=application,
        time_ps=time_ps,
        forces=forces,
        coordinates=coordinates,
        velocities=velocities,
        box_params=box_params,
    )
