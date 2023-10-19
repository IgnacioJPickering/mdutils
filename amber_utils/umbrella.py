from pathlib import Path
import typing as tp

from jinja2 import Environment, FileSystemLoader, select_autoescape

_TEMPLATES_PATH = Path(__file__).parent / "templates"

env = Environment(
    loader=FileSystemLoader(_TEMPLATES_PATH),
    autoescape=select_autoescape(),
    trim_blocks=True,
    lstrip_blocks=True,
)


class HarmonicRestraint:
    atom_indices: tp.Tuple[int, ...]
    residue_indices: tp.Tuple[int, ...]
    atom_names: tp.Tuple[str, ...]

    def _parse_indices(
        self,
        atom_indices: tp.Sequence[int] = (),
        residue_indices: tp.Sequence[int] = (),
        atom_names: tp.Sequence[str] = (),
        target_len: int = 0,
    ) -> tp.Tuple[tp.Tuple[int, ...], tp.Tuple[int, ...], tp.Tuple[str, ...]]:
        if atom_indices:
            if len(atom_indices) != target_len:
                raise ValueError(
                    f"Input sequence of atoms should have len {target_len}"
                )
            if residue_indices or atom_names:
                raise ValueError(
                    "One and only one of"
                    " residue_indices, atom_names or atom_indices should be specified"
                )
        elif residue_indices:
            if atom_indices or not atom_names:
                raise ValueError(
                    "One and only one of"
                    " residue_indices, atom_names or atom_indices should be specified"
                )
            if len(residue_indices) != target_len or len(atom_names) != target_len:
                raise ValueError(
                    f"Input sequence of atoms should have len {target_len}"
                )
        elif atom_names:
            if atom_indices or not residue_indices:
                raise ValueError(
                    "One and only one of"
                    " residue_indices, atom_names or atom_indices should be specified"
                )
            if len(residue_indices) != target_len or len(atom_names) != target_len:
                raise ValueError(
                    f"Input sequence of atoms should have len {target_len}"
                )
        else:
            raise ValueError(
                "One and only one of"
                " residue_indices, atom_names or atom_indices should be specified"
            )
        return tuple(atom_indices), tuple(residue_indices), tuple(atom_names)

    @property
    def atom_indices1(self) -> tp.Tuple[int, ...]:
        return tuple(a + 1 for a in self.atom_indices)

    @property
    def residue_indices1(self) -> tp.Tuple[int, ...]:
        return tuple(r + 1 for r in self.residue_indices)


class DistanceRestraint(HarmonicRestraint):
    def __init__(
        self,
        distance_ang: float,
        atom_indices: tp.Sequence[int] = (),
        residue_indices: tp.Sequence[int] = (),
        atom_names: tp.Sequence[str] = (),
        distance_slack_ang: float = 0.5,
        force_constant_amber_units: float = 200.0,  # kcalpermol / ang**2
    ):
        self.atom_indices, self.residue_indices, self.atom_names = self._parse_indices(
            atom_indices,
            residue_indices,
            atom_names,
            target_len=2,
        )

        if distance_ang - distance_slack_ang < 0.0:
            raise ValueError(
                "Distance restraint to small, increase distance or decrease slack"
            )

        self.distance_lower_bound = distance_ang - distance_slack_ang
        self.distance_lower_middle_bound = distance_ang
        self.distance_upper_middle_bound = distance_ang
        self.distance_upper_bound = distance_ang + distance_slack_ang
        self.lower_force_constant = force_constant_amber_units
        self.upper_force_constant = force_constant_amber_units


class AngleRestraint(HarmonicRestraint):
    def __init__(
        self,
        angle_deg: float,
        atom_indices: tp.Sequence[int] = (),
        residue_indices: tp.Sequence[int] = (),
        atom_names: tp.Sequence[str] = (),
        angle_slack_deg: float = 180.0,
        force_constant_amber_units_rad: float = 200.0,  # kcalpermol / rad**2
    ):
        self.atom_indices, self.residue_indices, self.atom_names = self._parse_indices(
            atom_indices,
            residue_indices,
            atom_names,
            target_len=3,
        )

        self.angle_lower_bound = angle_deg - angle_slack_deg
        self.angle_lower_middle_bound = angle_deg
        self.angle_upper_middle_bound = angle_deg
        self.angle_upper_bound = angle_deg + angle_slack_deg
        self.lower_force_constant = force_constant_amber_units_rad
        self.upper_force_constant = force_constant_amber_units_rad


class DihedralRestraint(HarmonicRestraint):
    def __init__(
        self,
        angle_deg: float,
        atom_indices: tp.Sequence[int] = (),
        residue_indices: tp.Sequence[int] = (),
        atom_names: tp.Sequence[str] = (),
        angle_slack_deg: float = 180.0,
        force_constant_amber_units_rad: float = 200.0,  # kcalpermol / rad**2
    ):
        self.atom_indices, self.residue_indices, self.atom_names = self._parse_indices(
            atom_indices,
            residue_indices,
            atom_names,
            target_len=4,
        )

        self.angle_lower_bound = angle_deg - angle_slack_deg
        self.angle_lower_middle_bound = angle_deg
        self.angle_upper_middle_bound = angle_deg
        self.angle_upper_bound = angle_deg + angle_slack_deg
        self.lower_force_constant = force_constant_amber_units_rad
        self.upper_force_constant = force_constant_amber_units_rad


def dump_harmonic_restraints(
    restraints: tp.Union[
        HarmonicRestraint,
        tp.Iterable[HarmonicRestraint],
    ],
    path: Path,
) -> None:
    path = Path(path)
    path.write_text(harmonic_restraints_block(restraints))


def harmonic_restraints_block(
    restraints: tp.Union[
        HarmonicRestraint,
        tp.Iterable[HarmonicRestraint],
    ],
) -> str:
    if isinstance(restraints, HarmonicRestraint):
        restraints = (restraints,)
    dihedral_restraints = []
    distance_restraints = []
    angle_restraints = []
    for restraint in restraints:
        if isinstance(restraint, DihedralRestraint):
            dihedral_restraints.append(restraint)
        elif isinstance(restraint, DistanceRestraint):
            distance_restraints.append(restraint)
        elif isinstance(restraint, AngleRestraint):
            angle_restraints.append(restraint)

    template_renderer = env.get_template("umbrella-harmonic.amber.restraints.jinja")
    return template_renderer.render(
        dihedral_restraints=dihedral_restraints,
        angle_restraints=angle_restraints,
        distance_restraints=distance_restraints,
    )
