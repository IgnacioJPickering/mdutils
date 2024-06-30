import pytest
from mdutils.dynamics import (
    Backend,
    Step,
    Ensemble,
    InitVel,
    calc_step_num,
    calc_time_ps,
    dump_rate_to_step_interval,
)


@pytest.mark.fast
def test_dump_rate_to_step_interval() -> None:
    assert dump_rate_to_step_interval("every-step") == 1
    assert dump_rate_to_step_interval("1 / 1") == 1
    assert dump_rate_to_step_interval("1 / 3") == 3
    assert dump_rate_to_step_interval("1 /3") == 3
    assert dump_rate_to_step_interval("1 / fs", 1) == 1
    assert dump_rate_to_step_interval("2 / fs", 1) == 1
    assert dump_rate_to_step_interval("1 /fs", 2) == 1
    assert dump_rate_to_step_interval("1 /fs", 0.1) == 10


@pytest.mark.fast
def test_enums() -> None:
    for enum in (Backend, Step, Ensemble, InitVel):
        assert all(isinstance(m.value, str) for m in enum)  # type: ignore


@pytest.mark.fast
def test_step_num() -> None:
    assert calc_step_num(0, 1) == 0
    assert calc_step_num(0, 2) == 0
    assert calc_step_num(1, 1) == 1000
    assert calc_step_num(1, 1000) == 1
    assert calc_step_num(1.5, 1) == 1500


@pytest.mark.fast
def test_time_ps() -> None:
    assert calc_time_ps(0, 1) == 0
    assert calc_time_ps(0, 2) == 0
    assert calc_time_ps(2, 0) == 0
    assert calc_time_ps(1000, 1) == 1
    assert calc_time_ps(2000, 1) == 2
    assert calc_time_ps(2500, 1) == 2.5
