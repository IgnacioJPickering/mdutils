from pathlib import Path
import pytest
import tempfile

from mdutils.amber import prmtop


@pytest.mark.fast
def testReconstructPrmtop() -> None:
    expect_prmtop = (Path(__file__).parent / "resources") / "test.prmtop"
    data = prmtop.load(expect_prmtop)
    with tempfile.TemporaryDirectory() as d:
        result_prmtop = Path(d) / "result.prmtop"
        prmtop.dump(data, result_prmtop, write_new_date=False)
        assert expect_prmtop.read_text() == result_prmtop.read_text()
