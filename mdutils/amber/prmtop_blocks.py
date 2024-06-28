from enum import Enum


class Format(Enum):
    INT_ARRAY = "10I8"  # integer
    ONE_INTEGER = "1I8"  # integer
    TWO_INTEGERS = "2I8"  # integer
    THREE_INTEGERS = "3I8"  # integer
    SIX_INTEGERS = "6I8"  # integer
    SMALL_INT_ARRAY = "20I4"  # integer
    STRING = "1A80"  # character
    SMALL_STRING_ARRAY = "20A4"  # character
    FLOAT_ARRAY = "5E16.8"  # float
    ONE_FLOAT = "1E16.8"  # float
    CMAP_FLOAT_ARRAY = "8F9.5"  # float


class Flag(Enum):
    # General
    TITLE = "TITLE"
    POINTERS = "POINTERS"
    # Node data
    ATOM_NAME = "ATOM_NAME"
    ATOMIC_NUMBER = "ATOMIC_NUMBER"
    AMBER_ATOM_TYPE = "AMBER_ATOM_TYPE"
    MASS = "MASS"
    # Node groups (residues)
    RESIDUE_LABEL = "RESIDUE_LABEL"
    # This is the starting atom on each re (1-idx)
    # Can be used to obtain residue sizes
    RESIDUE_POINTER = "RESIDUE_POINTER"

    # Node groups (solvent - solute)
    # Sets which residues are part of the same molecule, and which molecules
    # are "solvent" (must go at the end)
    ATOMS_PER_MOLECULE = "ATOMS_PER_MOLECULE"
    SOLVENT_POINTERS = "SOLVENT_POINTERS"
    # Valence interactions
    # Edges
    BONDS_WITH_HYDROGEN = "BONDS_INC_HYDROGEN"
    BONDS_WITHOUT_HYDROGEN = "BONDS_WITHOUT_HYDROGEN"
    BOND_FORCE_CONSTANT = "BOND_FORCE_CONSTANT"
    BOND_EQUIL_VALUE = "BOND_EQUIL_VALUE"
    # Angles
    ANGLES_WITH_HYDROGEN = "ANGLES_INC_HYDROGEN"
    ANGLES_WITHOUT_HYDROGEN = "ANGLES_WITHOUT_HYDROGEN"
    ANGLE_FORCE_CONSTANT = "ANGLE_FORCE_CONSTANT"
    ANGLE_EQUIL_VALUE = "ANGLE_EQUIL_VALUE"
    # dihedrals
    DIHEDRALS_WITH_HYDROGEN = "DIHEDRALS_INC_HYDROGEN"
    DIHEDRALS_WITHOUT_HYDROGEN = "DIHEDRALS_WITHOUT_HYDROGEN"
    DIHEDRAL_FORCE_CONSTANT = "DIHEDRAL_FORCE_CONSTANT"
    DIHEDRAL_PERIODICITY = "DIHEDRAL_PERIODICITY"
    DIHEDRAL_PHASE = "DIHEDRAL_PHASE"
    # Nonbonding interactions
    # Exclusion for nonbonded calculations
    # These two can be summarized in one ani-style neighborlist
    NUMBER_EXCLUDED_ATOMS = "NUMBER_EXCLUDED_ATOMS"
    EXCLUDED_ATOMS_LIST = "EXCLUDED_ATOMS_LIST"
    # Scale factors
    SCEE_SCALE_FACTOR = "SCEE_SCALE_FACTOR"
    SCNB_SCALE_FACTOR = "SCNB_SCALE_FACTOR"
    # Node data for nonbonded
    # Electrostatic
    CHARGE = "CHARGE"
    # lennard jones
    ATOM_TYPE_INDEX = "ATOM_TYPE_INDEX"  # lennard jones atom type index
    NONBONDED_PARM_INDEX = "NONBONDED_PARM_INDEX"
    LENNARD_JONES_ACOEF = "LENNARD_JONES_ACOEF"
    LENNARD_JONES_BCOEF = "LENNARD_JONES_BCOEF"
    # C4 stuff (usually not needed)
    LENNARD_JONES_CCOEF = "LENNARD_JONES_CCOEF"
    LENNARD_JONES_DCOEF = "LENNARD_JONES_DCOEF"
    LENNARD_JONES_DVALUE = "LENNARD_JONES_DVALUE"
    # 10-12 hbond (should be unused)
    HBOND_ACOEF = "HBOND_ACOEF"  # should be empty, but present
    HBOND_BCOEF = "HBOND_BCOEF"  # should be empty, but present
    HBCUT = "HBCUT"  # should be empty, but present
    # Polarizable ffs
    IPOL = "IPOL"  # boolean flag
    POLARIZABILITY = "POLARIZABILITY"  # Docs say 18.8, but it is a typo
    DIPOLE_DAMP_FACTOR = "DIPOLE_DAMP_FACTOR"  # Not mentioned in docs

    # Implicit solvent parameters and radii
    SCREEN = "SCREEN"  # screening Generalized Born parameters
    RADIUS_SET = "RADIUS_SET"  # String, kind of radii
    RADII = "RADII"  # GB radii values

    # Water cap information
    CAP_INFO = "CAP_INFO"  # 1 int, last atom before start of cap
    CAP_INFO2 = "CAP_INFO2"  # geometry of cap, 4 nums

    # CMAP related fields
    # Note that the cmaps can be found in the frcmod files
    # there seem to be "ff19sb" style cmaps, and "old" style cmaps
    # the ff19SB CMAPs seem to follow a pattern where they increase monotonically
    # in sequence within a given file,
    # and the resolution seems to always be "24"
    CMAP_COUNT = "CMAP_COUNT"
    CMAP_INDEX = "CMAP_INDEX"
    CMAP_RESOLUTION = "CMAP_RESOLUTION"  # just one int, always eq to 24 in ff19sb
    # There may be more than one of these, and they may have
    # Comment sections that specify the aminoacid
    # I believe these are always 24 x 24 arrays (this is the CMAP resolution)
    CMAP_PARAMETER_01 = "CMAP_PARAMETER_01"
    CMAP_PARAMETER_02 = "CMAP_PARAMETER_02"
    CMAP_PARAMETER_03 = "CMAP_PARAMETER_03"
    CMAP_PARAMETER_04 = "CMAP_PARAMETER_04"
    CMAP_PARAMETER_05 = "CMAP_PARAMETER_05"
    CMAP_PARAMETER_06 = "CMAP_PARAMETER_06"
    CMAP_PARAMETER_07 = "CMAP_PARAMETER_07"
    CMAP_PARAMETER_08 = "CMAP_PARAMETER_08"
    CMAP_PARAMETER_09 = "CMAP_PARAMETER_09"
    CMAP_PARAMETER_10 = "CMAP_PARAMETER_10"
    CMAP_PARAMETER_11 = "CMAP_PARAMETER_11"
    CMAP_PARAMETER_12 = "CMAP_PARAMETER_12"
    CMAP_PARAMETER_13 = "CMAP_PARAMETER_13"
    CMAP_PARAMETER_14 = "CMAP_PARAMETER_14"
    CMAP_PARAMETER_15 = "CMAP_PARAMETER_15"
    CMAP_PARAMETER_16 = "CMAP_PARAMETER_16"
    CMAP_PARAMETER_17 = "CMAP_PARAMETER_17"
    CMAP_PARAMETER_18 = "CMAP_PARAMETER_18"
    CMAP_PARAMETER_19 = "CMAP_PARAMETER_19"
    CMAP_PARAMETER_20 = "CMAP_PARAMETER_20"

    # Legacy (unused)
    SOLTY = "SOLTY"  # Zeros
    JOIN_ARRAY = "JOIN_ARRAY"  # Zeros
    IROTAT = "IROTAT"  # Zeros

    TREE_CHAIN_CLASSIFICATION = "TREE_CHAIN_CLASSIFICATION"  # Unused?

    # Only if box flag is set
    BOX_DIMENSIONS = "BOX_DIMENSIONS"  # Not zeros, but inpcrd values are used instead

    # Perturbation information
    # IAPERT = "IAPER"
    # ALMPER = "ALMPER"
    # PERT_POLARIZABILITY = "PERT_POLARIZABILITY"
    # PERT_CHARGE = "PERT_CHARGE"
    # PERT_ATOM_TYPE_INDEX = "PERT_ATOM_TYPE_INDEX"
    # PERT_ATOM_SYMBOL = "PERT_ATOM_SYMBOL"
    # PERT_ATOM_NAME = "PERT_ATOM_NAME"
    # PERT_RESIDUE_NAME = "PERT_RESIDUE_NAME"
    # PERT_DIHEDRAL_PARAMS = "PERT_DIHEDRAL_PARAMS"
    # PERT_DIHEDRAL_ATOMS = "PERT_DIHEDRAL_ATOMS"
    # PERT_ANGLE_PARAMS = "PERT_ANGLE_PARAMS"
    # PERT_ANGLE_ATOMS = "PERT_ANGLE_ATOMS"
    # PERT_BOND_PARAMS = "PERT_BOND_PARAMS"
    # PERT_BOND_ATOMS = "PERT_BOND_ATOMS"


CMAP_PARAMETER_FLAGS = {
    Flag.CMAP_PARAMETER_01,
    Flag.CMAP_PARAMETER_02,
    Flag.CMAP_PARAMETER_03,
    Flag.CMAP_PARAMETER_04,
    Flag.CMAP_PARAMETER_05,
    Flag.CMAP_PARAMETER_06,
    Flag.CMAP_PARAMETER_07,
    Flag.CMAP_PARAMETER_08,
    Flag.CMAP_PARAMETER_09,
    Flag.CMAP_PARAMETER_10,
    Flag.CMAP_PARAMETER_11,
    Flag.CMAP_PARAMETER_12,
    Flag.CMAP_PARAMETER_13,
    Flag.CMAP_PARAMETER_14,
    Flag.CMAP_PARAMETER_15,
    Flag.CMAP_PARAMETER_16,
    Flag.CMAP_PARAMETER_17,
    Flag.CMAP_PARAMETER_18,
    Flag.CMAP_PARAMETER_19,
    Flag.CMAP_PARAMETER_20,
}

FLAG_FORMAT_MAP = {
    Flag.CMAP_PARAMETER_01: Format.CMAP_FLOAT_ARRAY,
    Flag.CMAP_PARAMETER_02: Format.CMAP_FLOAT_ARRAY,
    Flag.CMAP_PARAMETER_03: Format.CMAP_FLOAT_ARRAY,
    Flag.CMAP_PARAMETER_04: Format.CMAP_FLOAT_ARRAY,
    Flag.CMAP_PARAMETER_05: Format.CMAP_FLOAT_ARRAY,
    Flag.CMAP_PARAMETER_06: Format.CMAP_FLOAT_ARRAY,
    Flag.CMAP_PARAMETER_07: Format.CMAP_FLOAT_ARRAY,
    Flag.CMAP_PARAMETER_08: Format.CMAP_FLOAT_ARRAY,
    Flag.CMAP_PARAMETER_09: Format.CMAP_FLOAT_ARRAY,
    Flag.CMAP_PARAMETER_10: Format.CMAP_FLOAT_ARRAY,
    Flag.CMAP_PARAMETER_11: Format.CMAP_FLOAT_ARRAY,
    Flag.CMAP_PARAMETER_12: Format.CMAP_FLOAT_ARRAY,
    Flag.CMAP_PARAMETER_13: Format.CMAP_FLOAT_ARRAY,
    Flag.CMAP_PARAMETER_14: Format.CMAP_FLOAT_ARRAY,
    Flag.CMAP_PARAMETER_15: Format.CMAP_FLOAT_ARRAY,
    Flag.CMAP_PARAMETER_16: Format.CMAP_FLOAT_ARRAY,
    Flag.CMAP_PARAMETER_17: Format.CMAP_FLOAT_ARRAY,
    Flag.CMAP_PARAMETER_18: Format.CMAP_FLOAT_ARRAY,
    Flag.CMAP_PARAMETER_19: Format.CMAP_FLOAT_ARRAY,
    Flag.CMAP_PARAMETER_20: Format.CMAP_FLOAT_ARRAY,
    Flag.TREE_CHAIN_CLASSIFICATION: Format.SMALL_STRING_ARRAY,
    Flag.IPOL: Format.ONE_INTEGER,
    Flag.POLARIZABILITY: Format.FLOAT_ARRAY,
    Flag.DIPOLE_DAMP_FACTOR: Format.FLOAT_ARRAY,
    Flag.SCREEN: Format.FLOAT_ARRAY,
    Flag.RADIUS_SET: Format.STRING,
    Flag.RADII: Format.FLOAT_ARRAY,
    Flag.CAP_INFO: Format.INT_ARRAY,
    Flag.CAP_INFO2: Format.FLOAT_ARRAY,
    Flag.CMAP_COUNT: Format.TWO_INTEGERS,
    Flag.CMAP_INDEX: Format.SIX_INTEGERS,
    Flag.CMAP_RESOLUTION: Format.SMALL_INT_ARRAY,
    Flag.BONDS_WITH_HYDROGEN: Format.INT_ARRAY,
    Flag.BONDS_WITHOUT_HYDROGEN: Format.INT_ARRAY,
    Flag.ANGLES_WITH_HYDROGEN: Format.INT_ARRAY,
    Flag.ANGLES_WITHOUT_HYDROGEN: Format.INT_ARRAY,
    Flag.DIHEDRALS_WITH_HYDROGEN: Format.INT_ARRAY,
    Flag.DIHEDRALS_WITHOUT_HYDROGEN: Format.INT_ARRAY,
    Flag.SOLTY: Format.FLOAT_ARRAY,
    Flag.JOIN_ARRAY: Format.INT_ARRAY,
    Flag.IROTAT: Format.INT_ARRAY,
    Flag.BOX_DIMENSIONS: Format.FLOAT_ARRAY,
    Flag.HBOND_BCOEF: Format.FLOAT_ARRAY,
    Flag.HBOND_ACOEF: Format.FLOAT_ARRAY,
    Flag.HBCUT: Format.FLOAT_ARRAY,
    Flag.SCEE_SCALE_FACTOR: Format.FLOAT_ARRAY,
    Flag.SCNB_SCALE_FACTOR: Format.FLOAT_ARRAY,
    Flag.BOND_FORCE_CONSTANT: Format.FLOAT_ARRAY,
    Flag.BOND_EQUIL_VALUE: Format.FLOAT_ARRAY,
    Flag.ANGLE_FORCE_CONSTANT: Format.FLOAT_ARRAY,
    Flag.ANGLE_EQUIL_VALUE: Format.FLOAT_ARRAY,
    Flag.NUMBER_EXCLUDED_ATOMS: Format.INT_ARRAY,
    Flag.EXCLUDED_ATOMS_LIST: Format.INT_ARRAY,
    Flag.DIHEDRAL_FORCE_CONSTANT: Format.FLOAT_ARRAY,
    Flag.DIHEDRAL_PERIODICITY: Format.FLOAT_ARRAY,
    Flag.DIHEDRAL_PHASE: Format.FLOAT_ARRAY,
    Flag.TITLE: Format.SMALL_STRING_ARRAY,
    Flag.POINTERS: Format.INT_ARRAY,
    Flag.ATOM_NAME: Format.SMALL_STRING_ARRAY,
    Flag.CHARGE: Format.FLOAT_ARRAY,
    Flag.ATOMIC_NUMBER: Format.INT_ARRAY,
    Flag.AMBER_ATOM_TYPE: Format.SMALL_STRING_ARRAY,
    Flag.MASS: Format.FLOAT_ARRAY,
    Flag.ATOM_TYPE_INDEX: Format.INT_ARRAY,
    Flag.NONBONDED_PARM_INDEX: Format.INT_ARRAY,
    Flag.LENNARD_JONES_ACOEF: Format.FLOAT_ARRAY,
    Flag.LENNARD_JONES_BCOEF: Format.FLOAT_ARRAY,
    Flag.LENNARD_JONES_CCOEF: Format.FLOAT_ARRAY,
    Flag.LENNARD_JONES_DCOEF: Format.THREE_INTEGERS,
    Flag.LENNARD_JONES_DVALUE: Format.ONE_FLOAT,
    Flag.RESIDUE_LABEL: Format.SMALL_STRING_ARRAY,
    Flag.RESIDUE_POINTER: Format.INT_ARRAY,
    Flag.SOLVENT_POINTERS: Format.THREE_INTEGERS,
    Flag.ATOMS_PER_MOLECULE: Format.INT_ARRAY,
}


HBOND_FLAGS = {
    Flag.HBOND_ACOEF,
    Flag.HBOND_BCOEF,
    Flag.HBCUT,
}


COVALENT_TERM_FLAGS = {
    Flag.BONDS_WITH_HYDROGEN,
    Flag.BONDS_WITHOUT_HYDROGEN,
    Flag.ANGLES_WITH_HYDROGEN,
    Flag.ANGLES_WITHOUT_HYDROGEN,
    Flag.DIHEDRALS_WITH_HYDROGEN,
    Flag.DIHEDRALS_WITHOUT_HYDROGEN,
}


LARGE_INTEGER_FORMATS = {
    Format.INT_ARRAY,
    Format.ONE_INTEGER,
    Format.TWO_INTEGERS,
    Format.THREE_INTEGERS,
    Format.SIX_INTEGERS,
}

LARGE_FLOAT_FORMATS = {
    Format.FLOAT_ARRAY,
    Format.ONE_FLOAT,
}
