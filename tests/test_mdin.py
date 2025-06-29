from pathlib import Path
import pytest
import io

import f90nml

from mdutils.amber.mdinput import (
    md,
    mixed_sdcg,
    AniArgs,
    MdArgs,
    MixedSdcgArgs,
)
from mdutils.ff import ImplicitFF
from mdutils.algorithm import LangevinThermo, BerendsenBaro, McBaro

_RESOURCES = Path(Path(__file__).parent, "resources")


@pytest.mark.fast
def test_remd_inputs() -> None:
    for temperature in (280, 290, 300, 310):
        input_str = md(
            MdArgs(
                shake=False,
                input_random_seed=1,
                time_ps=0.5,
                remd_time_interval_ps=0.05,
                implicit_solvent=ImplicitFF.VACUUM,
                thermo=LangevinThermo(temperature_kelvin=(temperature, temperature)),
            )
        )
        expect = f90nml.read(_RESOURCES / f"remd-{temperature}.mdin")
        actual = f90nml.read(io.StringIO(input_str))
        assert expect == actual


@pytest.mark.fast
def test_min_inputs() -> None:
    min_input_str = mixed_sdcg(MixedSdcgArgs(input_random_seed=1))
    expect_min = f90nml.read(_RESOURCES / "min.mdin")
    actual_min = f90nml.read(io.StringIO(min_input_str))
    assert expect_min == actual_min


@pytest.mark.fast
def test_md_inputs() -> None:
    nve_input_str = md(MdArgs(input_random_seed=1))
    expect_nve = f90nml.read(_RESOURCES / "nve-input.mdin")
    actual_nve = f90nml.read(io.StringIO(nve_input_str))
    assert expect_nve == actual_nve

    nvt_input_str = md(MdArgs(input_random_seed=1, thermo=LangevinThermo()))
    expect_nvt = f90nml.read(_RESOURCES / "nvt-input.mdin")
    actual_nvt = f90nml.read(io.StringIO(nvt_input_str))
    assert expect_nvt == actual_nvt

    npt_input_str = md(
        MdArgs(input_random_seed=1, thermo=LangevinThermo(), baro=McBaro())
    )
    expect_npt = f90nml.read(_RESOURCES / "npt-input.mdin")
    actual_npt = f90nml.read(io.StringIO(npt_input_str))
    assert expect_npt == actual_npt

    npt_berendsen_input_str = md(
        MdArgs(input_random_seed=1, thermo=LangevinThermo(), baro=BerendsenBaro())
    )
    expect_beren_npt = f90nml.read(_RESOURCES / "npt-berendsen-input.mdin")
    actual_beren_npt = f90nml.read(io.StringIO(npt_berendsen_input_str))
    assert expect_beren_npt == actual_beren_npt

    ani_input_str = md(
        MdArgs(
            input_random_seed=1, thermo=LangevinThermo(), baro=McBaro(), ani=AniArgs()
        )
    )
    (_RESOURCES / "ani.mdin").write_text(ani_input_str)
    expect_ani = f90nml.read(_RESOURCES / "ani.mdin")
    actual_ani = f90nml.read(io.StringIO(ani_input_str))
    assert expect_ani == actual_ani
