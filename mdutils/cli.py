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

import matplotlib as mpl
from mdutils.amber.prmtop import Prmtop, Flag
from mdutils.amber.traj import AmberTraj
from mdutils.paths import make_path_relative
from mdutils.remd import get_remd_trace, get_steps_num
from mdutils.constants import ATOMIC_NUMBER

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


# Taken from https://stackoverflow.com/questions/18926031/
# how-to-extract-a-subset-of-a-colormap-as-a-new-colormap-in-matplotlib
def truncate_colormap(
    cmap: mpl.colors.Colormap, minval: float = 0.0, maxval: float = 1.0, n: int = 100
) -> mpl.colors.Colormap:
    new_cmap = mpl.colors.LinearSegmentedColormap.from_list(
        "trunc({n},{a:.2f},{b:.2f})".format(n=cmap.name, a=minval, b=maxval),
        cmap(np.linspace(minval, maxval, n)),
    )
    return new_cmap


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
    ] = "K",
    y_label: tpx.Annotated[
        str,
        Option("--y-label", "--ylabel"),
    ] = "Temperature (K)",
    max_time_ps: tpx.Annotated[
        float,
        Option("-m", "--max-time-ps"),
    ] = 80.0,
) -> None:
    r"""Plot trips of the replicas for a remd simulation"""
    if path is None:
        path = Path.cwd()

    max_temp = 0.0
    min_temp = 0.0
    files = sorted(
        (p for p in path.iterdir() if p.is_dir() and p.name.endswith(suffix)),
        reverse=True,
    )
    replicas_num = len(files)
    # Assume all files have the same num steps
    all_temps = np.zeros((get_steps_num(files[0] / "mdcrd"), replicas_num))
    eye = np.eye(replicas_num)
    for i, p in enumerate(files):
        idxs, temps, times = get_remd_trace(p / "mdcrd")
        if not len(np.unique(temps)) == 1:
            all_temps[:, i] = temps
        else:
            one_hot = eye[idxs]
            all_temps = np.where(one_hot, temps[0], all_temps)
        max_temp = max(np.max(temps).item(), max_temp)
        min_temp = min(np.min(temps).item(), min_temp)

    # All times should be equivalent, so just get the last
    traces = {i: (all_temps[:, i], times) for i in range(replicas_num)}
    colors = [
        "#4E79A7",
        "#F28E2B",
        "#59A14F",
        "#AF7AA1",
        "#E15759",
        "#76B7B2",
        "#FFBE7D",
        "#79706E",
    ]

    fig, ax = plt.subplots()
    for idx, (trace, times) in traces.items():
        # Displace times slightly to differentiate lines in plot
        ax.plot(
            times + 0.01 * idx,
            trace,
            label=f"Replica {idx}",
            linewidth=1.0,
            color=colors[idx],
        )
    ax.set_xlabel(r"Time (ps)")
    ax.set_ylabel(y_label)
    ax.set_xlim(times[0], times[np.abs(times - (times[0] + max_time_ps)).argmin()])
    ax.legend(loc="upper right", framealpha=1.0)
    plt.show()


@app.command()
def rama(
    paths: tpx.Annotated[
        tp.Optional[tp.List[Path]], Argument(help="Root for the dynamics")
    ] = None,
    range_360: tpx.Annotated[
        bool,
        Option("--range-360/--no-range-360"),
    ] = False,
    plot: tpx.Annotated[
        bool,
        Option("--plot/--no-plot"),
    ] = True,
    add_residue_titles: tpx.Annotated[
        bool,
        Option("-a/-A", "--add-residue-titles/--no-add-residue-titles"),
    ] = True,
    bin_num: tpx.Annotated[
        int,
        Option("-b", "--bin-num"),
    ] = 80,
    add_contours: tpx.Annotated[
        bool,
        Option("--add-contours/--no-add-contours"),
    ] = True,
    selected_idxs: tpx.Annotated[
        tp.Optional[list[int]],
        Option("-i", "--idx"),
    ] = None,
    titles: tpx.Annotated[
        tp.Optional[tp.List[str]],
        Option("-t", "--title"),
    ] = None,
    vmin: tpx.Annotated[
        tp.Optional[float],
        Option("-v", "--vmin"),
    ] = None,
    vmax: tpx.Annotated[
        tp.Optional[float],
        Option("-v", "--vmax"),
    ] = None,
) -> None:
    # NOTE: Ramachandran plots are typically plotted in range [180, -180]
    if paths is None:
        paths = [Path.cwd()]
    if titles is None:
        titles = [p.stem for p in paths]
    for path, title in zip(paths, titles):
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
        prmtop = Prmtop.load(prmtop_fpath)
        residue_labels = prmtop.blocks[Flag.RESIDUE_LABEL]
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
            trunc_cmap = truncate_colormap(mpl.colormaps["jet"], minval=0.06)
            import pandas as pd

            for f in analysis_dir.iterdir():
                if _id in f.name and f.suffix == ".dat":
                    out_data = f
                    break
            else:
                raise RuntimeError("Output of analysis not found")
            df = pd.read_csv(out_data, sep=r"\s+")
            selected_residues = [
                int(col.split(":")[1])
                for col in df.columns
                if re.match(r"p[hs]i:\d+", col)
            ]
            _range = (
                [[-180, 180], [-180, 180]] if not range_360 else [[0, 360], [0, 360]]
            )
            ticks = list(
                range(-180, 180 + 45, 45) if not range_360 else range(0, 360 + 45, 45)
            )
            for residue_idx in sorted(set(selected_residues)):
                if selected_idxs and residue_idx not in selected_idxs:
                    continue
                x = df[f"phi:{residue_idx}"]
                y = df[f"psi:{residue_idx}"]
                bins, xedges, yedges = np.histogram2d(
                    x, y, bins=bin_num, range=_range, density=True
                )
                label = residue_labels[residue_idx].strip()
                fig, ax = plt.subplots()
                step = np.diff(xedges) / 2
                if add_contours:
                    ax.contour(
                        xedges[1:] - step,
                        yedges[1:] - step,
                        bins.T,
                        levels=3,
                        colors="k",
                        alpha=0.7,
                        linewidths=0.4,
                    )
                kwargs = {}
                if vmin is not None:
                    kwargs["vmin"] = vmin
                if vmax is not None:
                    kwargs["vmax"] = vmax
                _, _, _, img = ax.hist2d(
                    x,
                    y,
                    bins=bin_num,
                    cmap=trunc_cmap,
                    density=True,
                    rasterized=True,  # required to prevent grid in pdf/svg
                    range=_range,
                    **kwargs,
                )
                fig.colorbar(img, ax=ax)
                ax.set_xlabel(r"$\Phi$ (deg)")
                ax.set_ylabel(r"$\Psi$ (deg)")
                ax.set_xlim(ticks[0], ticks[-1])
                ax.set_ylim(ticks[0], ticks[-1])
                ax.set_xticks(ticks)
                ax.set_yticks(ticks)
                if add_residue_titles:
                    ax.set_title(f"{label}-{residue_idx}")
                plt.savefig(
                    f"/home/ipickering/Figures/{label}-{residue_idx}-{title}.pdf"
                )
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
    ] = True,
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
    # By default the temperature is untangled
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


# Print bond distances as a function of time
@app.command()
def bonds(
    prmtop_path: tpx.Annotated[
        tp.Optional[Path],
        Option("-p", "--prmtop", show_default=False),
    ] = None,
    mdcrd_path: tpx.Annotated[
        tp.Optional[Path],
        Option("-x", "--mdcrd", show_default=False),
    ] = None,
    _elements: tpx.Annotated[
        list[str] | None,
        Option("-e", "--element"),
    ] = None,
    _fftypes: tpx.Annotated[
        list[str] | None,
        Option("--fftype"),
    ] = None,
) -> None:
    if _fftypes is None:
        _fftypes = []
    if _elements is None:
        _elements = ["C", "C"]
    targ_fftypes = set(_fftypes)
    targ_elements = set(ATOMIC_NUMBER[s] for s in _elements)
    if len(targ_fftypes) > 2 or len(targ_elements) > 2:
        raise ValueError("More than 2 fftype or elements can't be specified")

    if prmtop_path is None:
        prmtop_path = Path.cwd()
    if mdcrd_path is None:
        mdcrd_path = Path.cwd()
    # Print bond distance, min bond distance max bond distance, average bond distance
    traj = AmberTraj.load(prmtop_path, mdcrd_path)
    if "H" in targ_elements or any(fftp.startswith("H") for fftp in targ_fftypes):
        bond_idxs = traj.prmtop.bonds.idxs_with_hydrogen
    else:
        bond_idxs = traj.prmtop.bonds.idxs_without_hydrogen

    bond_elements = traj.prmtop.atoms.znum[bond_idxs]
    bond_padded_fftypes = traj.prmtop.atoms.fftype[bond_idxs]
    _distances = []
    for idxs, elements, fftypes in zip(bond_idxs, bond_elements, bond_padded_fftypes):
        matches_fftypes = False
        matches_elements = False
        if not targ_fftypes or targ_fftypes == set(
            fftp.item().strip() for fftp in fftypes  # type: ignore
        ):
            matches_fftypes = True
        if not targ_elements or targ_elements == set(elements):  # type: ignore
            matches_elements = True
        if matches_fftypes and matches_elements:
            distance = traj.mdcrd.distance(idxs[0], idxs[1])  # type: ignore
            _distances.append(distance)
    all_distances = np.vstack(_distances)
    mean_dist = np.mean(all_distances, axis=0)
    max_dist = np.max(all_distances, axis=0)
    min_dist = np.min(all_distances, axis=0)
    fig, ax = plt.subplots()
    t = traj.mdcrd.time_ps
    ax.axhline(
        max_dist.max(),
        label="Max. distance",
        color="black",
        linestyle="dashed",
        alpha=0.5,
    )
    ax.plot(t, mean_dist, label="Mean distance", color="tab:green", alpha=0.5)
    ax.axhline(
        min_dist.min(),
        label="Min. distance",
        color="black",
        linestyle="dashed",
        alpha=0.5,
    )
    ax.set_ylabel(r"Distance ($\AA{}$)")
    ax.set_xlabel(r"Time (ps)")
    ax.set_xlim(t[0], t[-1])
    plt.show()


if __name__ == "__main__":
    app()
