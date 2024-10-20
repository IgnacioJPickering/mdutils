from pathlib import Path
import tempfile
import pytest

from mdutils.amber.inpcrd import Inpcrd


@pytest.mark.fast
def testReconstructInpcrd() -> None:
    expect_inpcrd = Path(Path(__file__).parent, "resources", "test.inpcrd")
    data = Inpcrd.load(expect_inpcrd)
    with tempfile.TemporaryDirectory() as d:
        result_inpcrd = Path(d) / "result.inpcrd"
        data.dump(result_inpcrd)
        assert result_inpcrd.read_text() == expect_inpcrd.read_text()
