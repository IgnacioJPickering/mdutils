from dataclasses import dataclass, asdict
import typing as tp
from pathlib import Path
import subprocess

import jinja2

from mdutils.amber.prmtop import Prmtop
from mdutils.aminoacid import AMINOACIDS_WITH_CO, AMINOACIDS


env = jinja2.Environment(
    loader=jinja2.FileSystemLoader(Path(__file__).parent / "cpptraj_templates"),
    undefined=jinja2.StrictUndefined,
    autoescape=jinja2.select_autoescape(),
    trim_blocks=True,
    lstrip_blocks=True,
)


@dataclass
class CpptrajCommonArgs:
    name: str
    traj_fpath: Path
    prmtop_fpath: Path
    sample_step: int = 1
    initial_frame: int = 0
    final_frame: tp.Union[tp.Literal["last"], int] = "last"


class CpptrajExecutor:
    # idx from 0 in constructor, as in python
    def __init__(
        self,
        name: str,
        prmtop_fpath: Path,
        traj_fpath: Path,
        initial_frame: int = 0,
        final_frame: tp.Union[tp.Literal["last"], int] = "last",
        sample_step: int = 1,
    ):
        # Displace final and initial frames, since cpptraj idxs from 1, as in fortran
        initial_frame += 1
        if initial_frame < 0:
            raise ValueError("initial_frame must be >= 0")
        if final_frame != "last":
            final_frame += 1
            if final_frame <= initial_frame:
                raise ValueError("final_frame must be > initial_frame")

        self._common_args = CpptrajCommonArgs(
            name=name,
            traj_fpath=traj_fpath,
            prmtop_fpath=prmtop_fpath,
            initial_frame=initial_frame,
            final_frame=final_frame,
            sample_step=sample_step,
        )
        self._prmtop = Prmtop.load(prmtop_fpath)

    def _write_buffers(
        self,
        out: subprocess.CompletedProcess[str],
        path: Path,
        suffix: str,
    ) -> None:
        path.with_suffix(f".{suffix}.stdout").write_text(out.stdout)
        path.with_suffix(f".{suffix}.stderr").write_text(out.stderr)

    def execute(
        self,
        cpptraj_block: str,
        cpptraj_input_path: Path,
    ) -> None:

        with open(cpptraj_input_path, mode="w+", encoding="utf-8") as f:
            f.write(cpptraj_block)

        out = subprocess.run(
            ["cpptraj", "-i", f"{cpptraj_input_path.name}"],
            cwd=cpptraj_input_path.parent,
            capture_output=True,
            text=True,
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
        last_solute_atom_idx1: int,
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
            last_solute_atom_idx1=last_solute_atom_idx1,
        )
        return render

    def hmr_input(
        self,
        out_prmtop_fpath: Path,
        modify_waters: bool,
    ) -> str:
        template = env.get_template("hmr.cpptraj.in.jinja")
        render = template.render(
            **asdict(self._common_args),
            out_prmtop_fpath=out_prmtop_fpath,
            modify_waters=modify_waters,
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
        res_labels = self._prmtop.resids.label
        mask_tuples: tp.List[tp.Tuple[str, str, str, str]] = []
        number_tuples: tp.List[tp.Tuple[int, int]] = []
        name_tuples: tp.List[tp.Tuple[str, str]] = []
        for j, (r, r_next) in enumerate(zip(res_labels[:-1], res_labels[1:])):
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
            analysis_name=(
                "peptidic-dihedrals" if not improper_torsion else "peptidic-impropers"
            ),
        )
        return render

    def out_of_plane_input(
        self,
        has_box: bool = True,
    ) -> str:
        template = env.get_template("out-of-plane.cpptraj.in.jinja")
        res_labels = self._prmtop.resids.label
        center_atoms: tp.List[str] = []
        plane_atoms: tp.List[tp.Tuple[str, str, str]] = []
        number_tuples: tp.List[tp.Tuple[int, int]] = []
        name_tuples: tp.List[tp.Tuple[str, str]] = []
        for j, (r, r_next) in enumerate(zip(res_labels[:-1], res_labels[1:])):
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
        res_labels = self._prmtop.resids.label
        masks: tp.Dict[str, str] = {}
        selected_residue_numbers: tp.List[int] = []
        selected_res_labels: tp.List[str] = []
        for j, r in enumerate(res_labels):
            if r.strip() in AMINOACIDS_WITH_CO:
                masks[f":{j + 1}@C"] = f":{j + 1}@O"
                selected_residue_numbers.append(j + 1)
                selected_res_labels.append(r.strip())
        render = template.render(
            **asdict(self._common_args),
            masks=masks,
            selected_residue_numbers=selected_residue_numbers,
            selected_residue_labels=selected_res_labels,
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
