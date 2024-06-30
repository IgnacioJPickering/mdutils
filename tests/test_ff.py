import pytest
from mdutils.ff import (
    FF,
    WaterFF,
    GeneralFF,
    ProteinFF,
    AniFF,
    ImplicitFF,
    PolarizableKind,
)


@pytest.mark.fast
def test_enums() -> None:
    for enum in (WaterFF, GeneralFF, ProteinFF, AniFF):
        assert all(isinstance(m.casefold(), str) for m in enum)  # type: ignore
        assert all(isinstance(m, FF) for m in enum)  # type: ignore


@pytest.mark.fast
def test_implicit() -> None:
    implicit = ImplicitFF.POISSON_BOLTZMANN
    assert implicit.mdin_idx == 10
    implicit = ImplicitFF.VACUUM
    assert implicit.mdin_idx == 6
    assert implicit is ImplicitFF.from_mdin_idx(6)


@pytest.mark.fast
def test_polarizable() -> None:
    kind = PolarizableKind.POLARIZABILITY_AND_DIPOLE_DAMP_FACTOR
    assert kind.prmtop_idx == 2
    kind = PolarizableKind.POLARIZABILITY
    assert kind.prmtop_idx == 1
    assert kind is PolarizableKind.from_prmtop_idx(1)
