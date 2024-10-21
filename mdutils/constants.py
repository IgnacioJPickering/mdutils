r"""Atomic and Density Functional constants

Values for electronegativity and hardness for elements H-Bk, all for neutral
atoms, and are taken from Table 3 of

Carlos Cardenas et. al. Benchmark Values of Chemical Potential and Chemical
Hardness for Atoms and Atomic Ions (Including Unstable Ions) from the Energies
of Isoelectronic Series.

DOI: 10.1039/C6CP04533B

Atomic masses supported are the first 119 elements, and are taken from:

Atomic weights of the elements 2013 (IUPAC Technical Report). Meija, J.,
Coplen, T., Berglund, M., et al. (2016). Pure and Applied Chemistry, 88(3), pp.
265-291. Retrieved 30 Nov. 2016, from doi:10.1515/pac-2015-0305

They are all consistent with those used in ASE

Covalent radii are in angstroms, and are are used for the
calculation of coordination numbers in DR. Taken
directly from Grimme et. al. dftd3 source code, in turn taken from Pyykko
and Atsumi, Chem. Eur. J. 15, 2009, 188-197
Values for metals decreased by 10 % with respect to Pyykko et. al.

Empirical Q in atomic units, correspond to sqrt(0.5 * sqrt(Z) * <r**2>/<r**4>).
In Grimme's code these are "r2r4", and are used to calculate the C8 values.
These are precalculated values. For details on their calculation consult the
DFTD3 papers

XTB repulsion data extracted from Grimme et. al. paper
https://pubs.acs.org/doi/10.1021/acs.jctc.8b01176
"""

from pathlib import Path
import json
import typing as tp

__all__ = [
    "ATOMIC_CONSTANTS",
    "ATOMIC_NUMBER",
    "ATOMIC_MASS",
    "ATOMIC_HARDNESS",
    "ATOMIC_COVALENT_RADIUS",
    "ATOMIC_SQRT_EMPIRICAL_CHARGE",
    "ATOMIC_ELECTRONEGATIVITY",
    "ATOMIC_XTB_REPULSION_ALPHA",
    "ATOMIC_XTB_REPULSION_YEFF",
    "MASS",
    "XTB_REPULSION_ALPHA",
    "XTB_REPULSION_YEFF",
    "COVALENT_RADIUS",
    "SQRT_EMPIRICAL_CHARGE",
    "HARDNESS",
    "ELECTRONEGATIVITY",
    "PERIODIC_TABLE",
]


with open(Path(__file__).parent.resolve() / "atomic_constants.json", mode="rt") as f:
    ATOMIC_CONSTANTS = json.load(f)


FF19SB_ATOMIC_MASS = {
    "C": 12.01,
    "Ca": 40.08,
    "H": 1.008,
    "F": 19.0,
    "Cl": 35.45,
    "Br": 79.9,
    "I": 126.9,
    "Mg": 24.305,
    "N": 14.01,
    "O": 16.0,
    "P": 30.97,
    "S": 32.06,
    "Cu": 63.55,
    "Fe": 55.0,
    "Zn": 65.4,
}


# Populate convenience variables here
ATOMIC_NUMBER: tp.Dict[str, int] = {}
ATOMIC_HARDNESS: tp.Dict[str, float] = {}
ATOMIC_ELECTRONEGATIVITY: tp.Dict[str, float] = {}
ATOMIC_MASS: tp.Dict[str, float] = {}
ATOMIC_SQRT_EMPIRICAL_CHARGE: tp.Dict[str, float] = {}
ATOMIC_COVALENT_RADIUS: tp.Dict[str, float] = {}
ATOMIC_XTB_REPULSION_ALPHA: tp.Dict[str, float] = {}
ATOMIC_XTB_REPULSION_YEFF: tp.Dict[str, float] = {}


for symbol, values in ATOMIC_CONSTANTS.items():
    if not symbol:
        continue
    znumber = values.get("znumber")
    hardness = values.get("hardness")
    electroneg = values.get("electronegativity")
    mass = values.get("mass")
    sqrt_empirical_charge = values.get("sqrt_empirical_charge")
    covalent_radius = values.get("covalent_radius")
    alpha = values.get("xtb_repulsion_alpha")
    yeff = values.get("xtb_repulsion_yeff")
    if znumber is not None:
        ATOMIC_NUMBER[symbol] = int(znumber)
    if hardness is not None:
        ATOMIC_HARDNESS[symbol] = float(hardness)
    if electroneg is not None:
        ATOMIC_ELECTRONEGATIVITY[symbol] = float(electroneg)
    if mass is not None:
        ATOMIC_MASS[symbol] = float(mass)
    if covalent_radius is not None:
        ATOMIC_COVALENT_RADIUS[symbol] = float(covalent_radius)
    if sqrt_empirical_charge is not None:
        ATOMIC_SQRT_EMPIRICAL_CHARGE[symbol] = float(sqrt_empirical_charge)
    if alpha is not None:
        ATOMIC_XTB_REPULSION_ALPHA[symbol] = float(alpha)
    if yeff is not None:
        ATOMIC_XTB_REPULSION_YEFF[symbol] = float(yeff)

# When indexed with the corresponding atomic number, PERIODIC_TABLE gives the
# element associated with it. Note that there is no element with atomic number
# 0, so "E" (extra pair) is returned in this case
PERIODIC_TABLE = tuple(
    kv[0] for kv in sorted(ATOMIC_NUMBER.items(), key=lambda x: x[1])
)


def mapping_to_znumber_indexed_seq(
    symbols_map: tp.Mapping[str, float]
) -> tp.Tuple[float, ...]:
    r"""
    Sort the values of {symbol: value} mapping by atomic number and output a
    tuple with the sorted values.

    All elements up to the highest present atomic number element must in the mapping.

    The first element (index 0) of the output will be NaN. Example:

    .. code-block:: python
        mapping = {"H": 3.0, "Li": 1.0, "He": 0.5 }
        znumber_indexed_seq = mapping_to_znumber_indexed_seq(mapping)
        # znumber_indexed_seq will be (NaN, 3.0, 0.5, 1.0)
    """
    _symbols_map = dict(symbols_map)
    seq = [0.0] * len(symbols_map)
    try:
        for k, v in _symbols_map.items():
            seq[ATOMIC_NUMBER[k]] = v
    except IndexError:
        raise ValueError(f"There are missing elements in {symbols_map}") from None
    return tuple(seq)


def znumber_indexed_seq_to_mapping(
    seq: tp.Sequence[float],
) -> tp.Dict[str, float]:
    r"""
    Inverse of mapping_to_znumber_indexed_list. The first element of the input
    must be 0.0. Example:

    .. code-block:: python
        znumber_indexed_seq = (0.0, 3.0, 0.5, 1.0)
        mapping = znumber_indexed_seq_to_mapping(znumber_indexed_seq)
        # mapping will be {"E": 0.0, "H": 3.0, "Li": 1.0, "He": 0.5 }
    """
    if not seq[0] == 0.0:
        raise ValueError("The first element of the input iterable must be 0.0")
    return {PERIODIC_TABLE[j]: v for j, v in enumerate(seq)}


# Create convenience tuples
MASS = mapping_to_znumber_indexed_seq(ATOMIC_MASS)
ELECTRONEGATIVITY = mapping_to_znumber_indexed_seq(ATOMIC_ELECTRONEGATIVITY)
HARDNESS = mapping_to_znumber_indexed_seq(ATOMIC_HARDNESS)
COVALENT_RADIUS = mapping_to_znumber_indexed_seq(ATOMIC_COVALENT_RADIUS)
SQRT_EMPIRICAL_CHARGE = mapping_to_znumber_indexed_seq(ATOMIC_SQRT_EMPIRICAL_CHARGE)
XTB_REPULSION_ALPHA = mapping_to_znumber_indexed_seq(ATOMIC_XTB_REPULSION_ALPHA)
XTB_REPULSION_YEFF = mapping_to_znumber_indexed_seq(ATOMIC_XTB_REPULSION_YEFF)
