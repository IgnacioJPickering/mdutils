from pathlib import Path
import tempfile
import pytest

from mdutils.amber.restart import Restart


@pytest.mark.fast
def testReconstructRestart() -> None:
    expect_restart = Path(Path(__file__).parent, "resources", "test.restart.nc")
    data = Restart.load(expect_restart)
    with tempfile.TemporaryDirectory() as d:
        result_restart = Path(d) / "result.restart.nc"
        data.dump(result_restart)
        assert result_restart.read_bytes() == expect_restart.read_bytes()
