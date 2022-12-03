from enum import Enum
from pathlib import Path
from typing import List, Any, Dict, Optional


class Format(Enum):
    INTEGER = "10I8"  # integer
    SENTENCE = "1a80"  # character
    ONE_INTEGER = "1I8"  # integer
    THREE_INTEGERS = "3I8"  # integer
    CHARACTERS = "20a4"  # character
    FLOAT = "5E16.8"  # float


class Flag(Enum):
    TITLE = "TITLE"
    POINTERS = "POINTERS"

    # node data
    ATOM_NAME = "ATOM_NAME"
    CHARGE = "CHARGE"
    ATOMIC_NUMBER = "ATOMIC_NUMBER"
    MASS = "MASS"
    AMBER_ATOM_TYPE = "AMBER_ATOM_TYPE"

    # lennard jones
    ATOM_TYPE_INDEX = "ATOM_TYPE_INDEX"  # lennard jones atom type index
    NONBONDED_PARM_INDEX = "NONBONDED_PARM_INDEX"
    LENNARD_JONES_ACOEF = "LENNARD_JONES_ACOEF"
    LENNARD_JONES_BCOEF = "LENNARD_JONES_BCOEF"

    # node groups (residues)
    RESIDUE_LABEL = "RESIDUE_LABEL"
    RESIDUE_POINTER = "RESIDUE_POINTER"

    # node groups (solvent - solute)
    SOLVENT_POINTERS = "SOLVENT_POINTERS"
    ATOMS_PER_MOLECULE = "ATOMS_PER_MOLECULE"

    # edges
    BONDS_INC_HYDROGEN = "BONDS_INC_HYDROGEN"
    BOND_FORCE_CONSTANT = "BOND_FORCE_CONSTANT"
    BOND_EQUIL_VALUE = "BOND_EQUIL_VALUE"

    # angles
    ANGLES_INC_HYDROGEN = "ANGLES_INC_HYDROGEN"
    ANGLES_WITHOUT_HYDROGEN = "ANGLES_WITHOUT_HYDROGEN"
    ANGLE_FORCE_CONSTANT = "ANGLE_FORCE_CONSTANT"
    ANGLE_EQUIL_VALUE = "ANGLE_EQUIL_VALUE"

    # exclusion for nonbonded calculations
    NUMBER_EXCLUDED_ATOMS = "NUMBER_EXCLUDED_ATOMS"
    EXCLUDED_ATOMS_LIST = "EXCLUDED_ATOMS_LIST"

    # dihedrals
    DIHEDRALS_INC_HYDROGEN = "DIHEDRALS_INC_HYDROGEN"
    DIHEDRALS_WITHOUT_HYDROGEN = "DIHEDRALS_WITHOUT_HYDROGEN"
    DIHEDRAL_FORCE_CONSTANT = "DIHEDRAL_FORCE_CONSTANT"
    DIHEDRAL_PERIODICITY = "DIHEDRAL_PERIODICITY"
    DIHEDRAL_PHASE = "DIHEDRAL_PHASE"

    SCEE_SCALE_FACTOR = "SCEE_SCALE_FACTOR"
    SCNB_SCALE_FACTOR = "SCNB_SCALE_FACTOR"

    # 10-12 hbond (unused)
    HBOND_ACOEF = "HBOND_ACOEF"
    HBOND_BCOEF = "HBOND_BCOEF"
    HBCUT = "HBCUT"

    # unused
    SOLTY = "SOLTY"
    JOIN_ARRAY = "JOIN_ARRAY"
    IROTAT = "IROTAT"

    TREE_CHAIN_CLASSIFICATION = "TREE_CHAIN_CLASSIFICATION"
    BOX_DIMENSIONS = "BOX_DIMENSIONS"  # unused section, better info in inpcrd
    SCREEN = "SCREEN"  # ???

    # polarizable ffs
    IPOL = "IPOL"
    POLARIZABILITY = "POLARIZABILITY"

    # implicit solvent radii
    RADIUS_SET = "RADIUS_SET"  # kind
    RADII = "RADII"  # values

    # cap
    CAP_INFO = "CAP_INFO"
    CAP_INFO2 = "CAP_INFO2"


_INTEGER_FORMATS = {Format.INTEGER, Format.ONE_INTEGER, Format.THREE_INTEGERS}


def read_block(prmtop: Path, flag: Flag) -> List[Any]:
    with open(prmtop, "r", encoding="utf-8") as f:
        in_block = False
        format_: Optional[Format] = None
        block = []
        for line in f:
            if not in_block:
                if line.startswith(f"%FLAG {flag.value}"):
                    in_block = True
            else:
                if line.startswith("%FORMAT"):
                    format_string = line.split("(")[-1].replace(")", "").strip()
                    format_ = Format(format_string)
                elif line.startswith("%FLAG"):
                    break
                else:
                    assert format_ is not None  # mypy
                    block.extend(_read_line_with_format(line, format_))
        return block


def _read_line_with_format(line: str, format_: Format) -> List[Any]:
    line = line[:-1]
    if format_ in _INTEGER_FORMATS:
        parsed_line = [int(line[i: i + 8]) for i in range(0, len(line), 8)]
    elif format_ is Format.FLOAT:
        parsed_line = [float(line[i: i + 16]) for i in range(0, len(line), 16)]
    elif format_ is Format.CHARACTERS:
        parsed_line = [line[i: i + 4] for i in range(0, len(line), 4)]
    elif format_ is Format.SENTENCE:
        parsed_line = [line]
    return parsed_line


def read_pointers(path: Path) -> Dict[str, int]:
    block = read_block(path, Flag.POINTERS)
    pointers = {}
    pointers["atoms"] = block[0]
    pointers["atom_types"] = block[1]
    pointers["bonds_with_hydrogen"] = block[2]
    pointers["bonds_without_hydrogen"] = block[3]
    pointers["angles_with_hydrogen"] = block[4]
    pointers["angles_without_hydrogen"] = block[5]
    pointers["dihedrals_with_hydrogen"] = block[6]
    pointers["dihedrals_without_hydrogen"] = block[7]
    # 8 and 9 unused
    pointers["excluded_atoms"] = block[10]
    pointers["residues"] = block[11]
    # 12, 13, 14 are equal to 3, 5, 7
    pointers["bond_types"] = block[15]
    pointers["angle_types"] = block[16]
    pointers["torsion_types"] = block[17]
    # 18 unused
    # 19 unused (10-12 H-bond pair types)
    # 20 set to 0, perturbation unused
    # 21 21 23 23 24 26 unused
    pointers["box_flag"] = block[27]
    pointers["atoms_in_largest_residue"] = block[28]
    pointers["cap_flag"] = block[29]
    pointers["extra_points"] = block[30]
    try:
        pointers["pimd_slices"] = block[31]
    except IndexError:
        pass
    return pointers
