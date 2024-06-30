import pytest

from mdutils.units import (
    NANOSECOND_TO_PICOSECOND,
    PICOSECOND_TO_NANOSECOND,
    FEMTOSECOND_TO_PICOSECOND,
    PICOSECOND_TO_FEMTOSECOND,
)


@pytest.mark.fast
def test_time_units() -> None:
    assert NANOSECOND_TO_PICOSECOND == 1000
    assert PICOSECOND_TO_NANOSECOND == 1.e-3
    assert PICOSECOND_TO_FEMTOSECOND == 1000
    assert FEMTOSECOND_TO_PICOSECOND == 1e-3
