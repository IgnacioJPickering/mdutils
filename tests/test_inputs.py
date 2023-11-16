import functools
from pathlib import Path
import itertools
import unittest

import amber_utils.inputs as amber_inputs
from amber_utils.barostats import (
    BerendsenBaro,
    McBaro,
)
from amber_utils.thermostats import (
    LangevinThermo,
    BerendsenThermo,
    SBerendsenThermo,
    AndersenThermo,
    OINHThermo,
    SINHThermo,
)
from amber_utils.inputs import (
    MdArgs,
    AniArgs,
    MixedSdcgArgs,
)

_DATA = Path(__file__).parent / "test_data"


# Fix random seed
MdArgs = functools.partial(MdArgs, random_seed=1)  # type: ignore
MixedSdcgArgs = functools.partial(MixedSdcgArgs, random_seed=1)  # type: ignore


class TestInputs(unittest.TestCase):
    def testSinglePoint(self) -> None:
        string = amber_inputs.single_point(MdArgs(torchani_args=AniArgs()))
        expect = (_DATA / "single_point_expect.amber.in").read_text()
        self.assertEqual(expect.rstrip(), string.rstrip())

    def testMixedSdcg(self) -> None:
        string = amber_inputs.mixed_sdcg(MixedSdcgArgs(torchani_args=AniArgs()))
        expect = (_DATA / "mixed_sdcg_expect.amber.in").read_text()
        self.assertEqual(expect.rstrip(), string.rstrip())

    def testNve(self) -> None:
        string = amber_inputs.nve(MdArgs(torchani_args=AniArgs()))
        expect = (_DATA / "nve_expect.amber.in").read_text()
        self.assertEqual(expect.rstrip(), string.rstrip())

    def testNvt(self) -> None:
        for thermo in (
            BerendsenThermo,
            AndersenThermo,
            LangevinThermo,
            OINHThermo,
            SINHThermo,
            SBerendsenThermo,
        ):
            fn_name = f"nvt_{thermo().name}"
            string = getattr(amber_inputs, fn_name)(
                MdArgs(torchani_args=AniArgs(), thermo=thermo())
            )
            expect = (_DATA / f"{fn_name}_expect.amber.in").read_text()
            self.assertEqual(expect.rstrip(), string.rstrip())

    def testNpt(self) -> None:
        for thermo, baro in itertools.product(
            (
                BerendsenThermo,
                AndersenThermo,
                LangevinThermo,
                OINHThermo,
                SINHThermo,
                SBerendsenThermo,
            ),
            (McBaro, BerendsenBaro),
        ):
            fn_name = f"npt_{thermo().name}_{baro().name}"
            string = getattr(amber_inputs, fn_name)(
                MdArgs(torchani_args=AniArgs(), thermo=thermo(), baro=baro())
            )
            expect = (_DATA / f"{fn_name}_expect.amber.in").read_text()
            self.assertEqual(expect.rstrip(), string.rstrip())


if __name__ == "__main__":
    unittest.main()
