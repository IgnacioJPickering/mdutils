import pytest
from mdutils.constants import (
    ATOMIC_MASS,
    ATOMIC_NUMBER,
    ATOMIC_HARDNESS,
    ATOMIC_COVALENT_RADIUS,
    ATOMIC_SQRT_EMPIRICAL_CHARGE,
    ATOMIC_ELECTRONEGATIVITY,
    ATOMIC_XTB_REPULSION_ALPHA,
    ATOMIC_XTB_REPULSION_YEFF,
    PERIODIC_TABLE,
    AMINOACIDS,
    MASS,
    ELECTRONEGATIVITY,
    HARDNESS,
    COVALENT_RADIUS,
    SQRT_EMPIRICAL_CHARGE,
    XTB_REPULSION_ALPHA,
    XTB_REPULSION_YEFF,
)


@pytest.mark.fast
def test_extra_pair() -> None:
    for seq in (
        MASS,
        HARDNESS,
        ELECTRONEGATIVITY,
        COVALENT_RADIUS,
        SQRT_EMPIRICAL_CHARGE,
        XTB_REPULSION_YEFF,
        XTB_REPULSION_ALPHA,
    ):
        assert seq[0] == 0.0

    for _map in (
        ATOMIC_MASS,
        ATOMIC_HARDNESS,
        ATOMIC_ELECTRONEGATIVITY,
        ATOMIC_COVALENT_RADIUS,
        ATOMIC_SQRT_EMPIRICAL_CHARGE,
        ATOMIC_XTB_REPULSION_YEFF,
        ATOMIC_XTB_REPULSION_ALPHA,
    ):
        assert _map["E"] == 0.0
    assert ATOMIC_NUMBER["E"] == 0
    assert PERIODIC_TABLE[0] == "E"


@pytest.mark.fast
def test_mass() -> None:
    assert MASS[1] == 1.008
    assert MASS[118] == 294.214
    assert ATOMIC_MASS["H"] == 1.008
    assert ATOMIC_MASS["Og"] == 294.214


@pytest.mark.fast
def test_numbers() -> None:
    assert PERIODIC_TABLE[1] == "H"
    assert PERIODIC_TABLE[118] == "Og"
    assert ATOMIC_NUMBER["H"] == 1
    assert ATOMIC_NUMBER["Og"] == 118


@pytest.mark.fast
def test_aminoacids() -> None:
    assert AMINOACIDS[0] == "ALA"
    assert AMINOACIDS[-1] == "NME"
