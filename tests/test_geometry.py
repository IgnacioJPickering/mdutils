import numpy as np
import pytest

from mdutils.geometry import NeighborlistKind, Scaling, Plane, BoxKind, BoxParams, bond_dist, bond_angle, dih_angle
from numpy.testing import assert_array_equal


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


@pytest.mark.fast
def test_geom_params() -> None:
    coords = np.array(
        [
            [0.7602522636, -0.0609579136, 0.0483331909],
            [-0.7320004592, 0.0455373733, -0.0764206792],
            [1.2458543313, -0.6204581625, -0.7578283571],
            [1.2162794535, 0.9554393715, 0.1535977060],
            [0.9643670382, -0.6311932658, 0.9898894811],
            [-1.0395388888, 1.0630463143, -0.4287016053],
            [-1.2554921430, -0.0898849024, 0.9033307732],
            [-1.1597215955, -0.6615288149, -0.8322005095],
        ]
    )

    dists_expect = np.array(
        [1.501240474721107, 1.1198620972341808,],
    )
    angles_expect = np.array(
        [110.65164016749473, 112.56027209457403,],
    )
    dihs_expect = np.array(
        [95.60273763479434, 112.11908933655107,]
    )
    dists = bond_dist(coords[[0, 1]], coords[[1, 7]])
    assert_array_equal(dists, dists_expect)
    angles = bond_angle(coords[[2, 6]], coords[[0, 1]], coords[[3, 0]])
    assert_array_equal(angles, angles_expect)
    dihs = dih_angle(coords[[6, 7]], coords[[1, 1]], coords[[0, 6]], coords[[3, 5]])
    assert_array_equal(dihs, dihs_expect)
