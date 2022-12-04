r"""Utilities to deal with amber-style netcdf restrt files"""

from pathlib import Path
from typing import Tuple, NamedTuple, Optional

import numpy as np
import netCDF4 as netcdf
from numpy.typing import NDArray

# data in restart files can optionally have velocities if it is the result of
# an MD, if it is the result of a min it only has coordinates


class AmberRestrtData(NamedTuple):
    name: str
    atoms_num: int
    coordinates: NDArray[np.float_]
    velocities: Optional[NDArray[np.float_]]
    box_lengths: NDArray[np.float_]
    box_angles: NDArray[np.float_]
    time: float


def read_coordinates_velocities_and_box(
    restrt: Path,
) -> Tuple[NDArray[np.float_], NDArray[np.float_], NDArray[np.float_]]:
    dataset = netcdf.Dataset(str(restrt), "r", format="NETCDF3_64BIT_OFFSET")
    cell_lengths = dataset["cell_lengths"][:].data
    cell_angles = dataset["cell_angles"][:].data
    coordinates = dataset["coordinates"][:].data
    try:
        velocities = dataset["velocities"][:].data
    except IndexError:
        velocities = None
    return coordinates, velocities, cell_lengths, cell_angles


def read_box(restrt: Path) -> Tuple[NDArray[np.float_], NDArray[np.float_]]:
    dataset = netcdf.Dataset(str(restrt), "r", format="NETCDF3_64BIT_OFFSET")
    cell_lengths = dataset["cell_lengths"][:].data
    cell_angles = dataset["cell_angles"][:].data
    return cell_lengths, cell_angles


def read_name_and_num_atoms(restrt: Path) -> Tuple[str, int]:
    dataset = netcdf.Dataset(str(restrt), "r", format="NETCDF3_64BIT_OFFSET")
    atoms_num = dataset["coordinates"].shape[0]
    name = dataset.title
    return name, atoms_num


def read_time(restrt: Path):
    dataset = netcdf.Dataset(str(restrt), "r", format="NETCDF3_64BIT_OFFSET")
    return dataset["time"][:].data.item()


def read_data(restrt: Path) -> AmberRestrtData:
    time = read_time(restrt)
    name, atoms_num = read_name_and_num_atoms(restrt)
    coordinates, velocities, box_lengths, box_angles = read_coordinates_velocities_and_box(restrt)
    return AmberRestrtData(name, atoms_num, coordinates, velocities, box_lengths, box_angles, time)
