from pathlib import Path
import pytest

from mdutils.amber import prmtop


@pytest.mark.fast
def testReconstructPrmtop() -> None:
    expect_prmtop = (Path(__file__).parent / "test_data") / "test.prmtop"
    data = prmtop.load(expect_prmtop)
    result_prmtop = Path(__file__).parent / "reconstructed.prmtop"
    prmtop.dump(data, result_prmtop, write_new_date=False)
    assert expect_prmtop.read_text() == result_prmtop.read_text()
    result_prmtop.unlink()
