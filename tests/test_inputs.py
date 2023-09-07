from pathlib import Path
import unittest
import amber_utils.inputs
from amber_utils.inputs import (
    MdArgs,
    NveArgs,
    AniArgs,
    MixedSdcgArgs,
    NvtLangevinArgs,
    NvtBerendsenArgs,
    NptBerendsenArgs,
)

_DATA = Path(__file__).parent / "test_data"


class TestInputs(unittest.TestCase):
    def testSinglePoint(self) -> None:
        string = amber_utils.inputs.single_point(MdArgs(torchani_args=AniArgs()))

        expect = (_DATA / "expect-single-point.amber.in").read_text()
        self.assertEqual(expect.rstrip(), string.rstrip())

    def testMixedSdcg(self) -> None:
        string = amber_utils.inputs.mixed_sdcg(MixedSdcgArgs(torchani_args=AniArgs()))
        expect = (_DATA / "expect-mixed-sdcg.amber.in").read_text()
        self.assertEqual(expect.rstrip(), string.rstrip())

    def testNve(self) -> None:
        string = amber_utils.inputs.nve(NveArgs(torchani_args=AniArgs()))
        expect = (_DATA / "expect-nve.amber.in").read_text()
        self.assertEqual(expect.rstrip(), string.rstrip())

    def testNvtLangevin(self) -> None:
        string = amber_utils.inputs.nvt_langevin(
            NvtLangevinArgs(torchani_args=AniArgs())
        )
        expect = (_DATA / "expect-nvt-langevin.amber.in").read_text()
        self.assertEqual(expect.rstrip(), string.rstrip())

    def testNvtBerendsen(self) -> None:
        string = amber_utils.inputs.nvt_berendsen(
            NvtBerendsenArgs(torchani_args=AniArgs())
        )
        expect = (_DATA / "expect-nvt-berendsen.amber.in").read_text()
        self.assertEqual(expect.rstrip(), string.rstrip())

    def testNptBerendsen(self) -> None:
        string = amber_utils.inputs.npt_berendsen(
            NptBerendsenArgs(torchani_args=AniArgs())
        )
        expect = (_DATA / "expect-npt-berendsen.amber.in").read_text()
        self.assertEqual(expect.rstrip(), string.rstrip())


if __name__ == "__main__":
    unittest.main()
