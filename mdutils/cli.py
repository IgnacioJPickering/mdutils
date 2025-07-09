import numpy as np
from pathlib import Path
import typing as tp
import typing_extensions as tpx
import subprocess
import warnings
import re

import jinja2
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


@app.command("untangle-tremd")
def untangle_tremd(
    path: tpx.Annotated[
        tp.Optional[Path],
        Option(
            "--path",
            show_default=False,
            help="Root path were T-REMD directories are located",
        ),
    ] = None,
    mdin_glob: tpx.Annotated[
        str,
        Option("--mdin-glob"),
    ] = "*mdin",
    prmtop_glob: tpx.Annotated[
        str,
        Option("--prmtop-glob"),
    ] = "*prmtop",
    first_replica_traj_name: tpx.Annotated[
        str,
        Option("--first-replica", help="Name of first replica"),
    ] = "mdcrd.000",
    cleanup: tpx.Annotated[
        bool,
        Option("--cleanup/--no-cleanup"),
    ] = True,
) -> None:
    # By default this function assumes a structure:
    #  - root
    #    - mdcrd.000 -> traj0/mdcrd
    #    - mdcrd.001 -> traj1/mdcrd
    #    - mdcrd.002 -> traj2/mdcrd
    #    - mdcrd.003 -> traj3/mdcrd
    #    - ...
    #    - traj0
    #      - mdcrd
    #      - mdin
    #      - prmtop
    #    - traj1
    #      - mdcrd
    #      - mdin
    #      - prmtop
    #    - traj2
    #      - mdcrd
    #      - mdin
    #      - prmtop
    #    - traj3
    #      - mdcrd
    #      - mdin
    #      - prmtop
    #    - ...
    _TEMPLATES_PATH = Path(__file__).parent / "cpptraj_templates"
    if path is None:
        path = Path.cwd()
    temps_kelvin = []
    prmtop_paths = []
    path = Path(__file__).parent
    for p in path.rglob(mdin_glob):
        prmtops = list(p.parent.glob(prmtop_glob))
        if len(prmtops) != 1:
            raise ValueError(f"No prmtop found in {p.parent}")
        prmtop_paths.append(prmtops[0])
        with open(p, mode="rt", encoding="utf-8") as f:
            for line in f:
                match = re.match(r".*temp0\s*=\s*([0-9.eE]+).*", line)
                if match:
                    temp_kelvin = float(match[1])
                    if not temp_kelvin.is_integer():
                        warnings.warn(
                            f"non-integer temperature {temp_kelvin} found in {p}"
                        )
                    temps_kelvin.append(temp_kelvin)
                    break
            else:
                raise ValueError(f"No temp0 found in {p}")

    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(_TEMPLATES_PATH),
        undefined=jinja2.StrictUndefined,
        autoescape=jinja2.select_autoescape(),
        trim_blocks=True,
        lstrip_blocks=True,
    )
    template = env.get_template("untangle-tremd.cpptraj.in.jinja")
    for temp, prmtop_path in zip(temps_kelvin, prmtop_paths):
        if temp.is_integer():
            temp_str = format(temp, ".0f")
        else:
            temp_str = str(temp).replace(".", "_")
        render = template.render(
            temp=temp,
            temp_str=temp_str,
            prmtop_name=str(prmtop_path.name),
            first_replica_traj_name=first_replica_traj_name,
        )
        cpptraj_in = path / f"untangle-tremd-{temp_str}.cpptraj.in"
        cpptraj_in.write_text(render)
        out = subprocess.run(
            ["cpptraj", cpptraj_in.name],
            cwd=cpptraj_in.parent,
            text=True,
            capture_output=True,
        )
        console.print(out.stdout)
        console.print(out.stderr)
        if out.returncode == 0 and cleanup:
            cpptraj_in.unlink()
