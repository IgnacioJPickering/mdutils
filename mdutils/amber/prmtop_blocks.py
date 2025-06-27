from enum import Enum


class Format(Enum):
    INT_ARRAY = "10I8"  # integer
    ONE_INTEGER = "1I8"  # integer
    TWO_INTEGERS = "2I8"  # integer
    THREE_INTEGERS = "3I8"  # integer
    SIX_INTEGERS_ARRAY = "6I8"  # integer
    SMALL_INT_ARRAY = "20I4"  # integer
    STRING = "1A80"  # character
    SMALL_STRING_ARRAY = "20A4"  # character
    FLOAT_ARRAY = "5E16.8"  # <=float32 prec
    ONE_FLOAT = "1E16.8"  # <=float32 prec
    CMAP_FLOAT_ARRAY = "8F9.5"  # <=float32 prec


# NOTE IMPORTANT!!! Order is used for printing (not sure if sander / pmemd
# support alt order, technically they should)
class Flag(Enum):
    # Global, general blocks
    NAME = "TITLE"
    POINTERS = "POINTERS"
    ATOM_LABEL = "ATOM_NAME"
    ATOM_CHARGE = "CHARGE"  # Electrostatics
    ATOM_ZNUM = "ATOMIC_NUMBER"
    ATOM_MASS = "MASS"
    ATOM_LJINDEX = "ATOM_TYPE_INDEX"  # "LJ" atom type index (fuses some fftype)
    NUMBER_EXCLUDED_ATOMS = "NUMBER_EXCLUDED_ATOMS"
    LJ_PARAM_INDEX = "NONBONDED_PARM_INDEX"  # idx into the LJ_PARAM arrays
    RESIDUE_LABEL = "RESIDUE_LABEL"
    RESIDUE_FIRST_ATOM_IDX1 = "RESIDUE_POINTER"  # Start atom of each, 1-idx
    BOND_FFTYPE_FORCE_CONSTANT = "BOND_FORCE_CONSTANT"
    BOND_FFTYPE_EQUIL_DISTANCE = "BOND_EQUIL_VALUE"
    ANGLE_FFTYPE_FORCE_CONSTANT = "ANGLE_FORCE_CONSTANT"
    ANGLE_FFTYPE_EQUIL_ANGLE = "ANGLE_EQUIL_VALUE"
    DIHEDRAL_FFTYPE_FORCE_CONSTANT = "DIHEDRAL_FORCE_CONSTANT"
    DIHEDRAL_FFTYPE_PERIODICITY = "DIHEDRAL_PERIODICITY"
    DIHEDRAL_FFTYPE_PHASE = "DIHEDRAL_PHASE"
    DIHEDRAL_FFTYPE_ELECTRO_ENDS_SCREEN = "SCEE_SCALE_FACTOR"  # Ends = 1-4 atoms
    DIHEDRAL_FFTYPE_LJ_ENDS_SCREEN = "SCNB_SCALE_FACTOR"  # Ends = 1-4 atoms
    ATOM_FFTYPE_LEGACY_SOLTY = "SOLTY"  # Unused, zeros, fftype-sized
    # Lennard Jones parameters
    # lj_param_idx[i, j]
    #  = lj_param_idx[num_ljtypes * ((atom_ljtype_idx[i] - 1) + atom_ljtype_idx[j])]
    LJ_PARAM_A = "LENNARD_JONES_ACOEF"
    LJ_PARAM_B = "LENNARD_JONES_BCOEF"
    # Bonded interactions
    # Edges
    BOND_WITH_HYDROGEN = "BONDS_INC_HYDROGEN"
    BOND_WITHOUT_HYDROGEN = "BONDS_WITHOUT_HYDROGEN"
    # Angles
    ANGLE_WITH_HYDROGEN = "ANGLES_INC_HYDROGEN"
    ANGLE_WITHOUT_HYDROGEN = "ANGLES_WITHOUT_HYDROGEN"
    # dihedrals
    DIHEDRAL_WITH_HYDROGEN = "DIHEDRALS_INC_HYDROGEN"
    DIHEDRAL_WITHOUT_HYDROGEN = "DIHEDRALS_WITHOUT_HYDROGEN"
    # Nonbonding interactions
    # Exclusion for nonbonded calculations
    # These two can be summarized in one ani-style neighborlist
    EXCLUDED_ATOMS_LIST = "EXCLUDED_ATOMS_LIST"
    # Hbond 10-12 interactions (legacy, should not be unused)
    HBOND_ACOEF = "HBOND_ACOEF"  # should be empty, but present
    HBOND_BCOEF = "HBOND_BCOEF"  # should be empty, but present
    HBCUT = "HBCUT"  # should be empty, but present
    # Nodes: atom-sized data
    ATOM_FFTYPE = "AMBER_ATOM_TYPE"
    ATOM_LEGACY_GRAPH_LABEL = "TREE_CHAIN_CLASSIFICATION"  # TODO: Not sure if unused
    ATOM_LEGACY_GRAPH_JOIN_IDX = "JOIN_ARRAY"  # Unused, Must be int = zeros
    ATOM_LEGACY_ROTATION_IDX = "IROTAT"  # Unused, Must be int = zeros
    # Molecule gruops ("SV/ST", no amber labels)
    SOLVENT_POINTERS = "SOLVENT_POINTERS"  # Solvent must go at the end
    # Groups of atoms (ress), residues (molecs) and molecs (solution-groups)
    # Node groups (residues)
    # Residue groups (not enforced in prmtop) ("molecules", no amber labels)
    ATOMS_PER_MOLECULE = "ATOMS_PER_MOLECULE"
    # NOTE BOX_DIMENSIONS is optional, must be present box flag is set, but it is unused
    BOX_DIMENSIONS = "BOX_DIMENSIONS"  # Not zeros, but unused
    RADIUS_SET = "RADIUS_SET"  # String, kind of implicit solvent radii, always present
    ATOM_IMPLSV_RADII = "RADII"  # Implicit solv radii, 'GB radii'
    ATOM_IMPLSV_SCREEN = "SCREEN"  # Implicit solv scren factor: 'GB screen'
    IPOL = "IPOL"  # Flag that marks the use of polarizable ff

    # TODO Not sure what the "std" order for these is, they are optional
    ATOM_POLARIZABILITY = "POLARIZABILITY"  # Only used for polarizable ff
    DIPOLE_DAMP = "DIPOLE_DAMP_FACTOR"  # TODO Not mentioned in the docs
    # Solvent cap view
    CAP_INFO = "CAP_INFO"  # Only if 'sv-cap' flag set. Last atom before start of cap
    CAP_INFO2 = "CAP_INFO2"  # Only if 'sv-cap' flag set: Geometry of cap, 4 nums
    # Lennard Jones C4 (usually not needed) TODO implement manipulation maybe?
    LJ_PARAM_C = "LENNARD_JONES_CCOEF"
    LJ_PARAM_D = "LENNARD_JONES_DCOEF"
    LJ_VALUE_D = "LENNARD_JONES_DVALUE"

    # TODO implement CMAP manipulation
    # CMAP related fields
    # Note that the cmaps can be found in the frcmod files
    # there seem to be "ff19sb" style cmaps, and "old" style cmaps
    # the ff19SB CMAPs seem to follow a pattern where they increase monotonically
    # in sequence within a given file,
    # and the resolution seems to always be "24"
    CMAP_COUNT = "CMAP_COUNT"
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
    CMAP_INDEX = "CMAP_INDEX"


# Perturbation information is not implemented:
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
    Flag.IPOL: Format.ONE_INTEGER,
    Flag.DIPOLE_DAMP: Format.FLOAT_ARRAY,
    Flag.RADIUS_SET: Format.STRING,
    Flag.CAP_INFO: Format.INT_ARRAY,
    Flag.CAP_INFO2: Format.FLOAT_ARRAY,
    Flag.CMAP_COUNT: Format.TWO_INTEGERS,
    Flag.CMAP_INDEX: Format.SIX_INTEGERS_ARRAY,
    Flag.CMAP_RESOLUTION: Format.SMALL_INT_ARRAY,
    Flag.BOND_WITH_HYDROGEN: Format.INT_ARRAY,
    Flag.BOND_WITHOUT_HYDROGEN: Format.INT_ARRAY,
    Flag.ANGLE_WITH_HYDROGEN: Format.INT_ARRAY,
    Flag.ANGLE_WITHOUT_HYDROGEN: Format.INT_ARRAY,
    Flag.DIHEDRAL_WITH_HYDROGEN: Format.INT_ARRAY,
    Flag.DIHEDRAL_WITHOUT_HYDROGEN: Format.INT_ARRAY,
    Flag.ATOM_FFTYPE_LEGACY_SOLTY: Format.FLOAT_ARRAY,
    Flag.BOX_DIMENSIONS: Format.FLOAT_ARRAY,
    Flag.HBOND_BCOEF: Format.FLOAT_ARRAY,
    Flag.HBOND_ACOEF: Format.FLOAT_ARRAY,
    Flag.HBCUT: Format.FLOAT_ARRAY,
    Flag.DIHEDRAL_FFTYPE_ELECTRO_ENDS_SCREEN: Format.FLOAT_ARRAY,
    Flag.DIHEDRAL_FFTYPE_LJ_ENDS_SCREEN: Format.FLOAT_ARRAY,
    Flag.BOND_FFTYPE_FORCE_CONSTANT: Format.FLOAT_ARRAY,
    Flag.BOND_FFTYPE_EQUIL_DISTANCE: Format.FLOAT_ARRAY,
    Flag.ANGLE_FFTYPE_FORCE_CONSTANT: Format.FLOAT_ARRAY,
    Flag.ANGLE_FFTYPE_EQUIL_ANGLE: Format.FLOAT_ARRAY,
    Flag.NUMBER_EXCLUDED_ATOMS: Format.INT_ARRAY,
    Flag.EXCLUDED_ATOMS_LIST: Format.INT_ARRAY,
    Flag.DIHEDRAL_FFTYPE_FORCE_CONSTANT: Format.FLOAT_ARRAY,
    Flag.DIHEDRAL_FFTYPE_PERIODICITY: Format.FLOAT_ARRAY,
    Flag.DIHEDRAL_FFTYPE_PHASE: Format.FLOAT_ARRAY,
    Flag.NAME: Format.SMALL_STRING_ARRAY,
    Flag.POINTERS: Format.INT_ARRAY,
    Flag.ATOM_POLARIZABILITY: Format.FLOAT_ARRAY,  # Docs say 18.8, but it is a typo
    Flag.ATOM_LABEL: Format.SMALL_STRING_ARRAY,
    Flag.ATOM_CHARGE: Format.FLOAT_ARRAY,
    Flag.ATOM_ZNUM: Format.INT_ARRAY,
    Flag.ATOM_FFTYPE: Format.SMALL_STRING_ARRAY,
    Flag.ATOM_MASS: Format.FLOAT_ARRAY,
    Flag.ATOM_IMPLSV_SCREEN: Format.FLOAT_ARRAY,
    Flag.ATOM_IMPLSV_RADII: Format.FLOAT_ARRAY,
    Flag.ATOM_LEGACY_GRAPH_LABEL: Format.SMALL_STRING_ARRAY,
    Flag.ATOM_LEGACY_GRAPH_JOIN_IDX: Format.INT_ARRAY,
    Flag.ATOM_LEGACY_ROTATION_IDX: Format.INT_ARRAY,
    Flag.ATOM_LJINDEX: Format.INT_ARRAY,
    Flag.LJ_PARAM_INDEX: Format.INT_ARRAY,
    Flag.LJ_PARAM_A: Format.FLOAT_ARRAY,
    Flag.LJ_PARAM_B: Format.FLOAT_ARRAY,
    Flag.LJ_PARAM_C: Format.FLOAT_ARRAY,
    Flag.LJ_PARAM_D: Format.THREE_INTEGERS,
    Flag.LJ_VALUE_D: Format.ONE_FLOAT,
    Flag.RESIDUE_LABEL: Format.SMALL_STRING_ARRAY,
    Flag.RESIDUE_FIRST_ATOM_IDX1: Format.INT_ARRAY,
    Flag.SOLVENT_POINTERS: Format.THREE_INTEGERS,
    Flag.ATOMS_PER_MOLECULE: Format.INT_ARRAY,
}


HBOND_FLAGS = {
    Flag.HBOND_ACOEF,
    Flag.HBOND_BCOEF,
    Flag.HBCUT,
}


LARGE_INTEGER_FORMATS = {
    Format.INT_ARRAY,
    Format.ONE_INTEGER,
    Format.TWO_INTEGERS,
    Format.THREE_INTEGERS,
}

LARGE_FLOAT_FORMATS = {
    Format.FLOAT_ARRAY,
    Format.ONE_FLOAT,
}

OPTIONAL_FLAGS = {
    # only if polarizable ff
    Flag.ATOM_POLARIZABILITY,
    Flag.DIPOLE_DAMP,
    # only if box and solv cap
    Flag.BOX_DIMENSIONS,
    Flag.CAP_INFO,
    Flag.CAP_INFO2,
    # only if C4
    Flag.LJ_PARAM_C,
    Flag.LJ_PARAM_D,
    Flag.LJ_VALUE_D,
    Flag.CMAP_COUNT,
    Flag.CMAP_INDEX,
    Flag.CMAP_RESOLUTION,
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
