import numpy as np
from pathlib import Path
import typing as tp
import typing_extensions as tpx

from rich.console import Console
from typer import Typer, Option, Argument

from mdutils.amber.prmtop import Prmtop, Flag

console = Console()
app = Typer()


@app.command()
def cat(
    prmtop_path: tpx.Annotated[Path, Argument()],
) -> None:
    # Dummy function that does nothing
    console.print(prmtop_path.read_text())


@app.command("increase-nonbonded")
def increase_nonbonded(
    prmtop_path: tpx.Annotated[Path, Argument()],
    out_path: tpx.Annotated[
        tp.Optional[Path],
        Option("-o", "--out-path", show_default=False),
    ] = None,
    factor: tpx.Annotated[
        int,
        Option("--factor"),
    ] = 4,
) -> None:
    # Dummy function that does nothing
    if out_path is None:
        out_path = prmtop_path.with_suffix(".increased.prmtop")
    prmtop = Prmtop.load(prmtop_path)
    num = prmtop.excluded_atoms_num
    # Make the excluded atoms list 10 times as large
    arr = prmtop.blocks[Flag.EXCLUDED_ATOMS_LIST]
    prmtop.blocks[Flag.EXCLUDED_ATOMS_LIST] = np.pad(
        arr, (0, (factor - 1) * num), mode="constant"
    )
    prmtop.dump(out_path)


@app.command("add-intra-bonds")
def add_intra_bonds(
    prmtop_path: tpx.Annotated[Path, Argument()],
    out_path: tpx.Annotated[
        tp.Optional[Path],
        Option("-o", "--out-path", show_default=False),
    ] = None,
) -> None:
    if out_path is None:
        out_path = prmtop_path.with_suffix(".intra.prmtop")
    prmtop = Prmtop.load(prmtop_path)
    prmtop.add_intra_molecule_bonds()
    prmtop.dump(out_path)


if __name__ == "__main__":
    app()
