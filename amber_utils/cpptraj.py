from dataclasses import dataclass, asdict
import typing as tp
from pathlib import Path
import subprocess

from jinja2 import Environment, FileSystemLoader, select_autoescape

from amber_utils.prmtop import read_block, Flag
from amber_utils.aminoacids import AMINOACIDS_WITH_CO, AMINOACIDS


templates_path = Path(__file__).parent.joinpath("cpptraj_templates")

env = Environment(
    loader=FileSystemLoader(templates_path),
    autoescape=select_autoescape(),
)


@dataclass
class CpptrajCommonArgs:
    name: str
    traj_fpath: Path
    prmtop_fpath: Path
    initial_frame: int
    final_frame: str
    sample_step: int


class CpptrajExecutor:
    def __init__(
        self,
        name: str,
        traj_fpath: Path,
        prmtop_fpath: Path,
        initial_frame: int = 0,
        final_frame: int = -1,
        sample_step: int = 1,
    ):
        if final_frame != -1:
            final_frame += 1
        if final_frame != -1 and final_frame <= 0:
            raise ValueError("Index of last frame should be strictly positive or -1")
        self._common_args = CpptrajCommonArgs(
            name=name,
            traj_fpath=traj_fpath,
            prmtop_fpath=prmtop_fpath,
            initial_frame=initial_frame + 1,
            final_frame=str(final_frame) if final_frame != -1 else "last",
            sample_step=sample_step,
        )

    def _write_buffers(
        self,
        out: subprocess.CompletedProcess[bytes],
        path: Path,
        suffix: str,
    ) -> None:
        stdout_path = path.with_suffix(f".{suffix}.stdout")
        stderr_path = path.with_suffix(f".{suffix}.stderr")

        with open(stdout_path, "w+", encoding="utf-8") as f:
            f.write(out.stdout.decode("utf-8"))

        with open(stderr_path, "w+", encoding="utf-8") as f:
            f.write(out.stderr.decode("utf-8"))

    def execute(
        self,
        cpptraj_block: str,
        cpptraj_input_path: Path,
    ) -> None:
        with open(cpptraj_input_path, "w+") as f:
            f.write(cpptraj_block)
            f.seek(0)
            out = subprocess.run(
                ["cpptraj", "-i", f"{cpptraj_input_path.name}"],
                cwd=cpptraj_input_path.parent,
                capture_output=True,
            )
            self._write_buffers(
                out, cpptraj_input_path.with_suffix("").with_suffix(""), "cpptraj"
            )
            out.check_returncode()

    def postprocess_input(
        self,
        autoimage: bool,
        strip_wat: bool,
        rms_fit: bool,
        last_solute_atom_iidx: int,
        out_traj_fpath: Path,
        out_prmtop_fpath: tp.Optional[Path],
        ref_fpath: tp.Optional[Path],
    ) -> str:
        template = env.get_template("postprocess.cpptraj.in.jinja")
        render = template.render(
            **asdict(self._common_args),
            autoimage=autoimage,
            strip_wat=strip_wat,
            out_traj_fpath=out_traj_fpath,
            rms_fit=rms_fit,
            ref_fpath=ref_fpath or "",
            out_prmtop_fpath=out_prmtop_fpath or "",
            last_solute_atom_iidx=last_solute_atom_iidx,
        )
        return render

    def diffusion_input(
        self,
        output_interval_ps: float,
        mask: str,
    ) -> str:
        template = env.get_template("diffusion.cpptraj.in.jinja")
        render = template.render(
            **asdict(self._common_args),
            output_interval_ps=f"{output_interval_ps:8.3}",
            mask=mask,
        )
        return render

    def peptidic_dihedrals_input(
        self,
        improper_torsion: bool = False,
        range_360: bool = False,
    ) -> str:
        template = env.get_template("peptidic-dihedrals.cpptraj.in.jinja")
        residue_names = read_block(
            self._common_args.prmtop_fpath, Flag.RESIDUE_LABEL
        )
        mask_tuples: tp.List[tp.Tuple[str, str, str, str]] = []
        number_tuples: tp.List[tp.Tuple[int, int]] = []
        name_tuples: tp.List[tp.Tuple[str, str]] = []
        for j, (r, r_next) in enumerate(zip(residue_names[:-1], residue_names[1:])):
            if (r.strip() in AMINOACIDS) and (r_next.strip() in AMINOACIDS):
                # the same definitions are used as the ones in AMBER's prep
                # files
                if improper_torsion:
                    if r_next.strip() == "NME":
                        next_carbon = "C"
                    else:
                        next_carbon = "CA"
                    mask_tuples.append(
                        (
                            f":{j + 1}@C",
                            f":{j + 2}@N",
                            f":{j + 2}@H",
                            f":{j + 2}@{next_carbon}",
                        )
                    )
                else:
                    mask_tuples.append(
                        (f":{j + 1}@O", f":{j + 1}@C", f":{j + 2}@N", f":{j + 2}@H")
                    )
                number_tuples.append((j + 1, j + 2))
                name_tuples.append((r.strip(), r_next.strip()))
        render = template.render(
            range_360=("range360" if range_360 else ""),
            **asdict(self._common_args),
            mask_tuples=mask_tuples,
            number_tuples=number_tuples,
            name_tuples=name_tuples,
            analysis_name="peptidic-dihedrals"
            if not improper_torsion
            else "peptidic-impropers",
        )
        return render

    def out_of_plane_input(
        self,
        has_box: bool = True,
    ) -> str:
        template = env.get_template("out-of-plane.cpptraj.in.jinja")
        residue_names = read_block(
            self._common_args.prmtop_fpath,
            Flag.RESIDUE_LABEL,
        )
        center_atoms: tp.List[str] = []
        plane_atoms: tp.List[tp.Tuple[str, str, str]] = []
        number_tuples: tp.List[tp.Tuple[int, int]] = []
        name_tuples: tp.List[tp.Tuple[str, str]] = []
        for j, (r, r_next) in enumerate(zip(residue_names[:-1], residue_names[1:])):
            if (r.strip() in AMINOACIDS) and (r_next.strip() in AMINOACIDS):
                center_atoms.append(f":{j + 2}@N")
                if r_next.strip() == "NME":
                    next_carbon = "C"
                else:
                    next_carbon = "CA"
                plane_atoms.append(
                    (f":{j + 1}@C", f":{j + 2}@H", f":{j + 2}@{next_carbon}")
                )
                number_tuples.append((j + 1, j + 2))
                name_tuples.append((r.strip(), r_next.strip()))
        render = template.render(
            **asdict(self._common_args),
            center_atoms=center_atoms,
            plane_atoms=plane_atoms,
            number_tuples=number_tuples,
            name_tuples=name_tuples,
            box_command="minimage" if has_box else "",
        )
        return render

    def carbonyls_input(self) -> str:
        template = env.get_template("carbonyls.cpptraj.in.jinja")
        residue_names = read_block(
            self._common_args.prmtop_fpath,
            Flag.RESIDUE_LABEL,
        )
        masks: tp.Dict[str, str] = {}
        selected_residue_numbers: tp.List[int] = []
        selected_residue_names: tp.List[str] = []
        for j, r in enumerate(residue_names):
            if r.strip() in AMINOACIDS_WITH_CO:
                masks[f":{j + 1}@C"] = f":{j + 1}@O"
                selected_residue_numbers.append(j + 1)
                selected_residue_names.append(r.strip())
        render = template.render(
            **asdict(self._common_args),
            masks=masks,
            selected_residue_numbers=selected_residue_numbers,
            selected_residue_names=selected_residue_names,
        )
        return render

    def phi_psi_input(
        self,
        range_360: bool = False,
    ) -> str:
        template = env.get_template("phi-psi.cpptraj.in.jinja")
        render = template.render(
            **asdict(self._common_args),
            range_360=("range360" if range_360 else ""),
        )
        return render

    def rdf_input(
        self,
        length_max_angstrom: float,
        bin_spacing_angstrom: float,
        solute_mask: str,
        solvent_mask: str,
    ) -> str:
        template = env.get_template("rdf.cpptraj.in.jinja")
        render = template.render(
            **asdict(self._common_args),
            length_max_angstrom=f"{length_max_angstrom:8.3}",
            bin_spacing_angstrom=f"{bin_spacing_angstrom:8.3}",
            solute_mask=solute_mask,
            solvent_mask=solvent_mask,
        )
        return render
