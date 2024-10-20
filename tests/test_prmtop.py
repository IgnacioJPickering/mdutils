from pathlib import Path
import pytest
import tempfile

from mdutils.amber.prmtop import Prmtop


@pytest.mark.fast
def testReconstructPrmtop() -> None:
    expect = (Path(__file__).parent / "resources") / "test.prmtop"
    prmtop = Prmtop.load(expect)
    with tempfile.TemporaryDirectory() as d:
        result = Path(d) / "result.prmtop"
        prmtop.dump(result, write_new_date=False)
        assert expect.read_text() == result.read_text()
