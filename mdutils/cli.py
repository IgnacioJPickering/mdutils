import shutil
import numpy as np
from pathlib import Path
import typing as tp
import typing_extensions as tpx
import subprocess
import warnings
import re
from uuid import uuid4

import jinja2
from rich.console import Console
from typer import Typer, Option, Argument
import matplotlib.pyplot as plt

from mdutils.amber.prmtop import Prmtop, Flag
from mdutils.paths import make_path_relative
from mdutils.remd import get_remd_trace

console = Console()
app = Typer()

_TEMPLATES_PATH = Path(__file__).parent / "cpptraj_templates"

env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(_TEMPLATES_PATH),
    undefined=jinja2.StrictUndefined,
    autoescape=jinja2.select_autoescape(),
    trim_blocks=True,
    lstrip_blocks=True,
)


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


@app.command("copy-prmtops")
def copy_prmtops(
    path: tpx.Annotated[tp.Optional[Path], Argument()] = None,
    prmtop_glob: tpx.Annotated[
        str,
        Option("--prmtop-glob"),
    ] = "*prmtop",
) -> None:
    r"""Recursively walk a subtree and convert all prmtop files that are symlinks
    to actual prmtop files
    """
    if path is None:
        path = Path.cwd()
    for d in path.rglob(prmtop_glob):
        if d.is_symlink():
            original = d.resolve(strict=True)
            d.unlink()
            shutil.copy2(original, d)


@app.command("remd-trips")
def remd_trips(
    path: tpx.Annotated[
        tp.Optional[Path], Argument(help="Root path where T-REMD dirs are located")
    ] = None,
    suffix: tpx.Annotated[
        str,
        Option("--suffix"),
    ] = "-remd-idx",
    y_label: tpx.Annotated[
        str,
        Option("--y-label", "--ylabel"),
    ] = "Temperature (K)",
) -> None:
    r"""Plot trips of the replicas for a remd simulation"""
    if path is None:
        path = Path.cwd()
    traces = {}
    for p in sorted(path.iterdir(), reverse=True):
        if p.is_dir() and p.name.endswith(suffix):
            idx, temps, times = get_remd_trace(p / "mdcrd")
            traces[idx] = (temps, times)

    fig, ax = plt.subplots()
    for idx, (trace, times) in traces.items():
        ax.plot(times, trace, label=f"Replica {idx}")
    ax.set_xlabel(r"Time (ps)")
    ax.set_ylabel(y_label)
    ax.legend(loc="upper right")
    plt.show()


@app.command()
def rama(
    path: tpx.Annotated[
        tp.Optional[Path], Argument(help="Root for the dynamics")
    ] = None,
    range_360: tpx.Annotated[
        bool,
        Option("--range-360/--no-range-360"),
    ] = False,
    plot: tpx.Annotated[
        bool,
        Option("--plot/--no-plot"),
    ] = True,
    bin_num: tpx.Annotated[
        int,
        Option("-b", "--bin-num"),
    ] = 60,
) -> None:
    # NOTE: Ramachandran plots are typically plotted in range [180, -180]
    if path is None:
        path = Path.cwd()
    template = env.get_template("phi-psi.cpptraj.in.jinja")
    prmtop_fpath = (path / "prmtop").resolve(strict=True)
    mdcrd_fpath = (path / "mdcrd").resolve(strict=True)

    _id = str(uuid4()).split("-")[0]
    render = template.render(
        traj_fpath=str(mdcrd_fpath),
        prmtop_fpath=str(prmtop_fpath),
        initial_frame=1,
        final_frame="last",
        range_360="range360" if range_360 else "",
        sample_step=1,
        name=f"rama-{_id}",
    )
    # TODO: Reduce code duplication here
    analysis_dir = path / "analysis"
    analysis_dir.mkdir(exist_ok=True)
    cpptraj_in = analysis_dir / f"phi-psi-{_id}.cpptraj.in"
    cpptraj_in.write_text(render)
    out = subprocess.run(
        ["cpptraj", cpptraj_in.name],
        cwd=analysis_dir,
        text=True,
        capture_output=True,
    )
    (analysis_dir / f"{_id}.stdout").write_text(out.stdout)
    (analysis_dir / f"{_id}.stderr").write_text(out.stderr)
    console.print(out.stdout)
    console.print(out.stderr)
    if plot:
        import pandas as pd

        for f in analysis_dir.iterdir():
            if _id in f.name and f.suffix == ".dat":
                out_data = f
                break
        else:
            raise RuntimeError("Output of analysis not found")
        df = pd.read_csv(out_data, sep=r"\s+")
        selected_residues = [
            int(col.split(":")[1]) for col in df.columns if re.match(r"p[hs]i:\d+", col)
        ]
        _range = [[-180, 180], [-180, 180]] if not range_360 else [[0, 360], [0, 360]]
        _ticks = range(-180, 180 + 45, 45) if not range_360 else range(0, 360 + 45, 45)
        ticks = list(_ticks)
        for residue_idx in sorted(set(selected_residues)):
            fig, ax = plt.subplots()
            _, _, _, img = ax.hist2d(
                df[f"phi:{residue_idx}"],
                df[f"psi:{residue_idx}"],
                bins=bin_num,
                cmap="jet",
                density=True,
                range=_range,
            )
            fig.colorbar(img, ax=ax)
            ax.set_xlabel(r"$\Phi$ (deg)")
            ax.set_ylabel(r"$\Psi$ (deg)")
            ax.set_xticks(ticks)
            ax.set_yticks(ticks)
            ax.set_title(f"Residue {residue_idx}")
            plt.show()


@app.command("untangle-remd")
def untangle_remd(
    path: tpx.Annotated[
        tp.Optional[Path], Argument(help="Root path where T-REMD dirs are located")
    ] = None,
    mdin_glob: tpx.Annotated[
        str,
        Option("--mdin-glob"),
    ] = "*mdin",
    prmtop_glob: tpx.Annotated[
        str,
        Option("--prmtop-glob"),
    ] = "*prmtop",
    mdcrd_glob: tpx.Annotated[
        str,
        Option("--mdcrd-glob"),
    ] = "*mdcrd",
    untangle_temp: tpx.Annotated[
        bool,
        Option("--untangle-temp/--no-untangle-temp"),
    ] = False,
) -> None:
    # By default this function assumes a structure:
    #  - root
    #    - traj-300K
    #      - mdcrd
    #      - mdin
    #      - prmtop
    #    - traj-310K
    #      - mdcrd
    #      - mdin
    #      - prmtop
    #    - traj-320K
    #      - mdcrd
    #      - mdin
    #      - prmtop
    #    - traj-330K
    #      - mdcrd
    #      - mdin
    #      - prmtop
    #    - ...
    # By default the "replica idx" is untangled. The temperature can be untangled by
    # passing --untangle-temp, but the default in Amber is to print untangled
    # temperatures
    untangle_kind = "temperature" if untangle_temp else "idx"
    if path is None:
        path = Path.cwd()
    values = []
    prmtop_paths = []
    mdcrd_paths = []
    for p in path.rglob(mdin_glob):
        prmtops = list(p.parent.glob(prmtop_glob))
        if len(prmtops) != 1:
            raise ValueError(f"No prmtop found in {p.parent}")
        mdcrds = list(p.parent.glob(mdcrd_glob))
        if len(mdcrds) != 1:
            raise ValueError(f"No mdcrd found in {p.parent}")
        mdcrd_paths.append(mdcrds[0].resolve())
        prmtop_paths.append(prmtops[0].resolve())
        if untangle_kind == "temperature":
            with open(p, mode="rt", encoding="utf-8") as f:
                for line in f:
                    match = re.match(r".*temp0\s*=\s*([0-9.eE]+).*", line)
                    if match:
                        temp_kelvin = float(match[1])
                        if not temp_kelvin.is_integer():
                            warnings.warn(
                                f"non-integer temperature {temp_kelvin} found in {p}"
                            )
                        values.append(temp_kelvin)
                        break
                else:
                    raise ValueError(f"No temp0 found in {p}")
    if untangle_kind == "idx":
        # Confusingly, cpptraj requires replica idx1, but inside netCDF the
        # value is idx0
        values = list(range(1, len(mdcrd_paths) + 1))
    template = env.get_template("untangle-remd.cpptraj.in.jinja")
    for val, prmtop_fpath in zip(values, prmtop_paths):
        if untangle_kind == "temperature":
            if val.is_integer():
                val_str = f"{val:.0f}K"
            else:
                val_str = f"{str(val).replace('.', '_')}K"
            dir_name = f"{val_str}-remd-temp"
        else:
            val_str = str(val - 1).zfill(3 if len(values) < 1000 else 4)
            dir_name = f"{val_str}-remd-idx"
        render = template.render(
            untangle_kind=untangle_kind,
            value=val,
            prmtop_name=str(prmtop_fpath),
            first_replica_traj_name=str(mdcrd_paths[0]),
            replica_traj_names=",".join(map(str, mdcrd_paths[1:])),
        )
        out_dir = path / dir_name
        out_dir.mkdir()
        cpptraj_in = out_dir / "untangle-remd.cpptraj.in"
        cpptraj_in.write_text(render)
        out = subprocess.run(
            ["cpptraj", cpptraj_in.name],
            cwd=out_dir,
            text=True,
            capture_output=True,
        )
        (out_dir / "prmtop").symlink_to(make_path_relative(out_dir, prmtop_fpath))
        console.print(out.stdout)
        console.print(out.stderr)


if __name__ == "__main__":
    app()
