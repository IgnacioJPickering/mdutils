from pathlib import Path
import tempfile
import pytest
from dataclasses import asdict

import numpy as np

from mdutils.amber.restart import Restart


@pytest.mark.fast
def testReconstructRestart() -> None:
    expect_restart = Path(Path(__file__).parent, "resources", "test.restart.nc")
    data = Restart.load(expect_restart)
    with tempfile.TemporaryDirectory() as d:
        result_restart = Path(d) / "test.restart.nc"
        data.dump(result_restart)
        newdata = Restart.load(result_restart)
        for k, newattr in asdict(newdata).items():
            if isinstance(newattr, np.ndarray):
                assert (getattr(data, k) == newattr).all()
            else:
                assert getattr(data, k) == newattr
        assert result_restart.read_bytes() == expect_restart.read_bytes()
