import math
import typing as tp
from pathlib import Path


def write_groupfile_block(
    prefixes: tp.Optional[tp.Sequence[str]] = None,
    temperatures_kelvin: tp.Optional[tp.Sequence[int]] = None,
    do_remd: bool = False,
    ascii_inpcrd: bool = True,
    ascii_output: bool = False,
    share_inpcrd: bool = True,
    share_prmtop: bool = True,
) -> str:
    if prefixes is None and temperatures_kelvin is None:
        raise ValueError(
            "At least one of 'prefixes' and 'temperatures' must be specified"
        )
    if prefixes is None:
        assert temperatures_kelvin is not None
        prefixes = [f"{t}K." for t in temperatures_kelvin]
    assert prefixes is not None

    lines = []
    for i, prefix in enumerate(prefixes):
        parts = [
            "-O",
            "-rem",
            "1" if do_remd else "0",
            "-p",
            f"{'' if share_prmtop else prefix}prmtop",
            "-i",
            f"{prefix}mdin",
            "-inf",
            f"{prefix}mdinfo",
            "-o",
            f"{prefix}mdout",
            "-r",
            f"{prefix}restart{'.nc' if ascii_output else ''}",
            "-x",
            f"{prefix}mdcrd{'.nc' if ascii_output else ''}",
            "-c",
            f"{'' if share_inpcrd else prefix}inpcrd{'' if ascii_inpcrd else '.nc'}",
        ]
        if do_remd:
            parts.extend(["-remlog", "rem.log"])
        if i == len(prefixes) - 1:
            parts.append("\n")
        lines.append(" ".join(parts))
    return "\n".join(lines)


def dump_groupfile(
    path: Path,
    prefixes: tp.Optional[tp.Sequence[str]] = None,
    temperatures_kelvin: tp.Optional[tp.Sequence[int]] = None,
    do_remd: bool = False,
    ascii_inpcrd: bool = True,
    ascii_output: bool = False,
    share_inpcrd: bool = True,
    share_prmtop: bool = True,
) -> None:
    Path(path).write_text(
        write_groupfile_block(
            prefixes,
            temperatures_kelvin,
            do_remd,
            ascii_inpcrd,
            ascii_output,
            share_inpcrd,
            share_prmtop,
        )
    )


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


# TODO: Use geomspace instead of this
# To recover the values from the original article (Met-Enkephaline) use
# num=8, lo=200, hi=700, num_below=0
# Which results in [200, 239, 286, 342, 409, 489, 585, 700]
def seq_of_temperature_kelvin_from_temperature_range(
    replicas_num: int,
    temperature_kelvin_lo: int = 300,
    temperature_kelvin_hi: int = 630,
    num_below: int = 1,  # How many temperatures to add below the low part of the range
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
