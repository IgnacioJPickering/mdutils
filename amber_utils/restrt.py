r"""Utilities to deal with amber-style netcdf restrt files"""
import typing as tp
from pathlib import Path

import numpy as np
import netCDF4 as netcdf
from numpy.typing import NDArray

from amber_utils.units import AMBER_VELOCITIES_SCALE_FACTOR


# Data in restart files can optionally have velocities or forces if it is the
# result of an MD, if it is the result of a min it only has coordinates
class AmberRestrtData(tp.NamedTuple):
    name: str
    atoms_num: int
    time_ps: float
    coordinates: NDArray[np.float_]
    velocities: tp.Optional[NDArray[np.float_]]
    forces: tp.Optional[NDArray[np.float_]]
    box_lengths: tp.Optional[NDArray[np.float_]]
    box_angles: tp.Optional[NDArray[np.float_]]


def write(
    restrt: Path,
    time_ps: float,
    coordinates: NDArray[np.float_],
    forces: tp.Optional[NDArray[np.float_]] = None,
    velocities: tp.Optional[NDArray[np.float_]] = None,
    box_lengths: tp.Optional[NDArray[np.float_]] = None,
    box_angles: tp.Optional[NDArray[np.float_]] = None,
    name: str = "restrt",
    program: str = "mdrun",
) -> None:
    if (box_lengths is not None and box_angles is None) or (
        box_angles is not None and box_lengths is None
    ):
        raise ValueError("Box lengths and box angles should both be present")
    dataset = netcdf.Dataset(str(restrt), "w", format="NETCDF3_64BIT_OFFSET")

    # Global Attributes
    dataset.Conventions = "AMBERRESTART"
    dataset.ConventionVersion = "1.0"
    dataset.program = program
    dataset.programVersion = "0.1"

    # Optional Global Attributes
    dataset.application = "mdrun"
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

    if box_lengths is not None:
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
        dataset["cell_lengths"][:] = box_lengths
        dataset["cell_angles"][:] = box_angles


def read_coordinates_velocities_forces_and_box(
    restrt: Path,
) -> tp.Tuple[
    NDArray[np.float_],
    tp.Optional[NDArray[np.float_]],
    tp.Optional[NDArray[np.float_]],
    tp.Optional[NDArray[np.float_]],
    tp.Optional[NDArray[np.float_]],
]:
    dataset = netcdf.Dataset(str(restrt), "r", format="NETCDF3_64BIT_OFFSET")
    coordinates = dataset["coordinates"][:].data
    try:
        cell_lengths = dataset["cell_lengths"][:].data
        cell_angles = dataset["cell_angles"][:].data
    except IndexError:
        cell_lengths = None
        cell_angles = None
    try:
        velocities = dataset["velocities"][:].data * AMBER_VELOCITIES_SCALE_FACTOR
    except IndexError:
        velocities = None
    try:
        forces = dataset["forces"][:].data
    except IndexError:
        forces = None
    return coordinates, forces, velocities, cell_lengths, cell_angles


def read_coordinates_velocities_and_box(
    restrt: Path,
) -> tp.Tuple[
    NDArray[np.float_],
    tp.Optional[NDArray[np.float_]],
    tp.Optional[NDArray[np.float_]],
    tp.Optional[NDArray[np.float_]],
]:
    dataset = netcdf.Dataset(str(restrt), "r", format="NETCDF3_64BIT_OFFSET")
    coordinates = dataset["coordinates"][:].data
    try:
        cell_lengths = dataset["cell_lengths"][:].data
        cell_angles = dataset["cell_angles"][:].data
    except IndexError:
        cell_lengths = None
        cell_angles = None
    try:
        velocities = dataset["velocities"][:].data * AMBER_VELOCITIES_SCALE_FACTOR
    except IndexError:
        velocities = None
    return coordinates, velocities, cell_lengths, cell_angles


def read_box(
    restrt: Path,
) -> tp.Tuple[tp.Optional[NDArray[np.float_]], tp.Optional[NDArray[np.float_]]]:
    dataset = netcdf.Dataset(str(restrt), "r", format="NETCDF3_64BIT_OFFSET")
    try:
        cell_lengths = dataset["cell_lengths"][:].data
        cell_angles = dataset["cell_angles"][:].data
    except IndexError:
        cell_lengths = None
        cell_angles = None
    return cell_lengths, cell_angles


def read_name_and_num_atoms(restrt: Path) -> tp.Tuple[str, int]:
    dataset = netcdf.Dataset(str(restrt), "r", format="NETCDF3_64BIT_OFFSET")
    atoms_num = dataset["coordinates"].shape[0]
    name = dataset.title
    return name, atoms_num


def read_time(restrt: Path) -> float:
    dataset = netcdf.Dataset(str(restrt), "r", format="NETCDF3_64BIT_OFFSET")
    return dataset["time"][:].data.item()


def read_data(restrt: Path) -> AmberRestrtData:
    time_ps = read_time(restrt)
    name, atoms_num = read_name_and_num_atoms(restrt)
    (
        coordinates,
        velocities,
        forces,
        box_lengths,
        box_angles,
    ) = read_coordinates_velocities_forces_and_box(restrt)
    return AmberRestrtData(
        name=name,
        atoms_num=atoms_num,
        time_ps=time_ps,
        forces=forces,
        coordinates=coordinates,
        velocities=velocities,
        box_lengths=box_lengths,
        box_angles=box_angles,
    )
