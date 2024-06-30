from pathlib import Path
import unittest

from mdutils.amber import prmtop


class TestPrmtop(unittest.TestCase):
    def testReconstructPrmtop(self) -> None:
        expect_prmtop = (Path(__file__).parent / "test_data") / "test.prmtop"
        data = prmtop.load(expect_prmtop)
        result_prmtop = Path(__file__).parent / "reconstructed.prmtop"
        prmtop.dump(data, result_prmtop, write_new_date=False)
        self.assertEquals(expect_prmtop.read_text(), result_prmtop.read_text())
