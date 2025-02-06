import pytest
from mdutils.geometry import Scaling, Plane
from mdutils.algorithm import (
    OptimKind,
    BaroKind,
    BerendsenBaro,
    McBaro,
    TensionKind,
    McTension,
    ThermoKind,
    BerendsenThermo,
    AndersenThermo,
    OINHThermo,
    SINHThermo,
    LangevinThermo,
    BussiThermo,
)


@pytest.mark.fast
def test_enums() -> None:
    for e in (OptimKind, ThermoKind, BaroKind, TensionKind):
        assert all(isinstance(member.value, str) for member in e)


@pytest.mark.fast
def test_thermos() -> None:
    for thermo in (
        BerendsenThermo(),
        AndersenThermo(),
        OINHThermo(),
        SINHThermo(),
        LangevinThermo(),
        BussiThermo(),
    ):
        assert thermo.temperature_kelvin == (300.0, 300.0)
        assert bool(thermo.name)


@pytest.mark.fast
def test_baros() -> None:
    for baro in (
        BerendsenBaro(),
        McBaro(),
    ):
        assert baro.pressure_bar == (1.0, 1.0)
        assert baro.scaling == Scaling.ISOTROPIC
        assert bool(baro.name)


@pytest.mark.fast
def test_tension() -> None:
    for tension in (McTension(),):
        assert tension.tension_dyne_per_cm == 1.0
        assert tension.plane == Plane.XY
        assert tension.interface_num == 2
