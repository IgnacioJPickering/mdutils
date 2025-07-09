from pathlib import Path
import typing as tp
import math

import netCDF4 as netcdf
from numpy.typing import NDArray
import numpy as np


def get_remd_trace(path: Path) -> tuple[int, NDArray[np.float64], NDArray[np.float64]]:
    # Returns a tuple with the replica index and associated target temperatures
    # throughout the dynamics
    netcdf_ds = netcdf.Dataset(str(path), "r", format="NETCDF3_64BIT_OFFSET")
    temps_kelvin = netcdf_ds["remd_values"][:]
    times_ps = netcdf_ds["time"][:].astype(np.float64)
    idxs = netcdf_ds["remd_repidx"][:]
    if not len(np.unique(idxs)) == 1:
        raise ValueError("More than one replica idx found in dataset")
    idx = idxs[0].item()
    return (idx, temps_kelvin, times_ps)


# TODO: This is incorrect, the actual way to get it uses the sqrt but is not direct
def replicas_from_atom_num(atom_num: int) -> int:
    replicas_num = max(int(round(math.sqrt(atom_num))), 2)
    # Make sure the number of replicas is even
    if replicas_num % 2 == 1:
        replicas_num += 1
    return replicas_num


def seq_of_temperature_kelvin_from_atom_num(
    atom_num: int,
    initial_temperature_kelvin: tp.Optional[int] = None,
    factor: float = 1.10,  # Recommended to be 1.05-1.10
) -> list[int]:
    return seq_of_temperature_kelvin(
        replicas_from_atom_num(atom_num), initial_temperature_kelvin, factor
    )


# Geometric series: T[i] = T[0] * r^i with r = 1.05-1.10 (lets do 1.10)
# This is the recommended way of obtaining T sequences in REMD
def seq_of_temperature_kelvin(
    replicas_num: int,
    initial_temperature_kelvin: tp.Optional[int] = None,
    factor: float = 1.10,  # Recommended to be 1.05-1.10
) -> list[int]:
    if replicas_num % 2 == 1:
        raise ValueError("The number of replicas must be even")
    if initial_temperature_kelvin is None:
        initial_temperature_kelvin = int(round(300.0 / factor))
    temperatures = []
    for i in range(replicas_num):
        temperatures.append(int(round(initial_temperature_kelvin * factor**i)))
    return temperatures


# To recover the values from the original article (Met-Enkephaline) use
# num=8, lo=200, hi=700, num_below=0
# Which results in [200, 239, 286, 342, 409, 489, 585, 700]
# and a factor of 1.19
def seq_of_temperature_kelvin_from_temperature_range(
    replicas_num: int,
    temperature_kelvin_lo: int = 300,
    temperature_kelvin_hi: int = 630,
    num_below: int = 0,  # How many temperatures to add below the low part of the range
    verbose: bool = False,
) -> list[int]:
    factor = (temperature_kelvin_hi / temperature_kelvin_lo) ** (
        1 / (replicas_num - num_below - 1)
    )
    if verbose:
        print(f"Using factor {factor:.4f}")
    if replicas_num % 2 == 1:
        raise ValueError("The number of replicas must be even")
    initial_temperature_kelvin = int(round(temperature_kelvin_lo / factor**num_below))
    return seq_of_temperature_kelvin(replicas_num, initial_temperature_kelvin, factor)


def seq_of_temperature_kelvin_from_temperature_range_and_atom_num(
    atom_num: int,
    temperature_kelvin_lo: int = 300,
    temperature_kelvin_hi: int = 630,
    num_below: int = 1,
    verbose: bool = False,
) -> list[int]:
    return seq_of_temperature_kelvin_from_temperature_range(
        replicas_from_atom_num(atom_num),
        temperature_kelvin_lo,
        temperature_kelvin_hi,
        num_below,
        verbose,
    )
