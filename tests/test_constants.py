import pytest
from mdutils.constants import ATOMIC_MASS, ATOMIC_NUMBER, PERIODIC_TABLE, AMINOACIDS


@pytest.mark.fast
def test_mass() -> None:
    assert ATOMIC_MASS["H"] == 1.008
    assert ATOMIC_MASS["Og"] == 294.214


@pytest.mark.fast
def test_numbers() -> None:
    assert ATOMIC_NUMBER["H"] == 1
    assert ATOMIC_NUMBER["Og"] == 118


@pytest.mark.fast
def test_aminoacids() -> None:
    assert AMINOACIDS[0] == "ALA"
    assert AMINOACIDS[-1] == "NME"


@pytest.mark.fast
def test_periodic_table() -> None:
    assert PERIODIC_TABLE[1] == "H"
    assert PERIODIC_TABLE[118] == "Og"
