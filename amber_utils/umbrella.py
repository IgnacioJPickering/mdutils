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


class DistanceHarmonicRestraint:
    def __init__(
        self,
        atom_indices: tp.Sequence[int],
        distance_ang: float,
        distance_slack_ang: float = 2.0,
        force_constant_amber_units: float = 200.0,  # kcalpermol / ang**2
    ):
        if len(atom_indices) != 2:
            raise ValueError("Input sequence of atoms should have len 4")
        self.atom_indices = atom_indices
        self.atom_indices1 = [a + 1 for a in atom_indices]
        self.distance_lower_bound = distance_ang - distance_slack_ang
        self.distance_lower_middle_bound = distance_ang
        self.distance_upper_middle_bound = distance_ang
        self.distance_upper_bound = distance_ang + distance_slack_ang
        self.lower_force_constant = force_constant_amber_units
        self.upper_force_constant = force_constant_amber_units


class DihedralHarmonicRestraint:
    def __init__(
        self,
        atom_indices: tp.Sequence[int],
        angle_deg: float,
        angle_slack_deg: float = 180.0,
        force_constant_amber_units_rad: float = 200.0,  # kcalpermol / rad**2
    ):
        if len(atom_indices) != 4:
            raise ValueError("Input sequence of atoms should have len 4")
        self.atom_indices = atom_indices
        self.atom_indices1 = [a + 1 for a in atom_indices]
        self.angle_lower_bound = angle_deg - angle_slack_deg
        self.angle_lower_middle_bound = angle_deg
        self.angle_upper_middle_bound = angle_deg
        self.angle_upper_bound = angle_deg + angle_slack_deg
        self.lower_force_constant = force_constant_amber_units_rad
        self.upper_force_constant = force_constant_amber_units_rad


def harmonic_dihedral_restraints(
    restraints: tp.Union[
        DihedralHarmonicRestraint,
        tp.Iterable[DihedralHarmonicRestraint],
    ],
) -> str:
    if isinstance(restraints, DihedralHarmonicRestraint):
        restraints = (restraints,)

    template_renderer = env.get_template("umbrella-dihedrals.amber.restraints.jinja")
    return template_renderer.render(restraints=restraints)
