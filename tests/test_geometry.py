import numpy as np
import pytest

from mdutils.geometry import NeighborlistKind, Scaling, Plane, BoxKind, BoxParams


@pytest.mark.fast
def test_enums() -> None:
    for enum in (NeighborlistKind, Scaling, Plane, BoxKind):
        assert all(isinstance(m.value, str) for m in enum)  # type: ignore


@pytest.mark.fast
def test_box_params() -> None:
    expect_lengths = np.array([1.0, 1.0, 1.0], dtype=np.float64)
    expect_angles = np.array([90.0, 90.0, 90.0], dtype=np.float64)
    params = BoxParams()
    assert (expect_lengths == params.lengths).all()
    assert (expect_angles == params.angles).all()
    assert expect_lengths.dtype == np.float64
    assert expect_angles.dtype == np.float64


@pytest.mark.fast
def test_box_and_plane_kinds() -> None:
    plane = Plane.XY
    assert plane.prmtop_idx == 3
    assert Plane.from_prmtop_idx(3) is plane

    box_kind = BoxKind.NO_BOX
    assert box_kind.prmtop_idx == 0
    assert BoxKind.from_prmtop_idx(0) is box_kind
