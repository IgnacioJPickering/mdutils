import math
import typing_extensions as tpx
from collections import defaultdict
import datetime
import typing as tp
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from mdutils.constants import PERIODIC_TABLE, FF19SB_ATOMIC_MASS, ATOMIC_MASS
from mdutils.geometry import BoxKind, SolvCapKind
from mdutils.units import AMBER_ATOM_CHARGE_SCALE_FACTOR
from mdutils.ff import PolarizableKind
from mdutils.amber.prmtop_blocks import (
    Format,
    Flag,
    FLAG_FORMAT_MAP,
    LARGE_FLOAT_FORMATS,
    LARGE_INTEGER_FORMATS,
    HBOND_FLAGS,
    OPTIONAL_FLAGS,
)

__all__ = [
    "PrmtopMeta",
    "Prmtop",
    "load_single_raw_prmtop_block",
]


class PrmtopError(ValueError):
    pass


# Meta is fetched from "POINTERS" and "TITLE" blocks in the prmtop file
@dataclass
class PrmtopMeta:
    version: str
    date_time: str
    # System size
    atoms_num: int
    resids_num: int
    resids_max_atoms_num: int
    # Bonded interactions, with H: bond, angle, dihedral
    bond_with_hydrogen_num: int
    angle_with_hydrogen_num: int
    dihedral_with_hydrogen_num: int
    # Bonded interactions, no H: bond, angle, dihedral
    bond_without_hydrogen_num: int
    angle_without_hydrogen_num: int
    dihedral_without_hydrogen_num: int
    # Distinct ljindex for atom
    atom_ljindex_num: int
    # Distinct fftype for atom, bond, angle, dihedral
    atom_fftype_num: int
    bond_fftype_num: int
    angle_fftype_num: int
    dihedral_fftype_num: int
    # Exclusion list
    excluded_atoms_num: int
    # Extra points
    extra_points_num: int
    # Box and solv-cap enums
    box_kind: BoxKind
    solv_cap_kind: SolvCapKind
    # Path Integral MD (PIMD) slices (optional)
    pimd_slices_num: tp.Optional[int] = None

    def __post_init__(self) -> None:
        # Check well-formedness of the POINTERS block
        # TODO: check for excluded atoms num and pimd slices?
        if not (0 <= self.extra_points_num):
            raise PrmtopError("Extra points num should be >= 0")
        if not (1 <= self.atoms_num):
            raise PrmtopError("At least 1 atom is required")
        if not (1 <= self.atom_ljindex_num):
            raise PrmtopError("At least 1 ljindex is required")
        if not (1 <= self.atom_fftype_num):
            raise PrmtopError("At least 1 fftype is required")

        if not (1 <= self.resids_num <= self.atoms_num):
            raise PrmtopError("Bad num residues, must be between 1 and num atoms")

        largest_possible_residue = self.atoms_num - (self.resids_num - 1)
        if not (1 <= self.resids_max_atoms_num <= largest_possible_residue):
            raise PrmtopError("Impossible num atoms in largest residue")
        for prefix in ("bond", "angle", "dihedral"):
            key_with = f"{prefix}_with_hydrogen_num"
            key_without = f"{prefix}_without_hydrogen_num"
            key_ff = f"{prefix}_fftype_num"
            val_with = getattr(self, key_with)
            val_without = getattr(self, key_without)
            val_ff = getattr(self, key_ff)
            if val_with < 0 or val_without < 0 or val_ff < 0:
                raise PrmtopError(f"{key_with}, {key_without}, {key_ff} should be > 0")
            if val_with + val_without > 0 and val_ff == 0:
                raise PrmtopError("No {key_ff} implies {key_with}, {key_without} = 0")

    @property
    def has_box(self) -> bool:
        return self.box_kind is not BoxKind.NO_BOX

    @property
    def has_solv_cap(self) -> bool:
        return self.solv_cap_kind is not SolvCapKind.NO_SOLV_CAP

    @classmethod
    def load(cls, path: Path) -> tpx.Self:
        r"""
        Load amber prmtop metadata

        The metadata is the POINTERS block, together with the name (title), the
        version and date. Note that technically the order of the blocks in a prmtop
        file can be arbitrary, and if the first blocks are not meta blocks, it may
        be slow to read the metadata.
        """
        version = "V0001.000"
        date_time = ""
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                if line.startswith("%VERSION"):
                    parts = line.split()[1:]
                    version = parts[2]
                    date_time = f"{parts[5]}  {parts[6]}"
                    break

        block = load_single_raw_prmtop_block(path, Flag.POINTERS)
        # Check well-formedness of the POINTERS block
        if bool(block[8]):
            raise RuntimeError("NHPARM not supported, value should be 0")
        # (only sander.LES accepts prmtop created by addles)
        if bool(block[9]):
            raise RuntimeError("Prmtops of ADDLES fmt not supported, value should be 0")
        if block[12] != block[3] or block[13] != block[5] or block[14] != block[7]:
            raise RuntimeError("Constraints not supported, they should not be present")
        if bool(block[19]):
            raise RuntimeError("HBOND terms not supported, they should not be present")
        if any(bool(b) for b in block[20:27]):
            raise RuntimeError("Pert info not supported, values 20-27 should be 0")
        return cls(
            version=version,
            date_time=date_time,
            # Atoms
            atoms_num=block[0],
            atom_ljindex_num=block[1],  # Num distinct ljindex for atoms
            # Bonded interactions, with and without H: bond, angle, dihedral
            bond_with_hydrogen_num=block[2],
            bond_without_hydrogen_num=block[3],
            angle_with_hydrogen_num=block[4],
            angle_without_hydrogen_num=block[5],
            dihedral_with_hydrogen_num=block[6],
            dihedral_without_hydrogen_num=block[7],
            # Misc
            excluded_atoms_num=block[10],  # Exclusion list
            resids_num=block[11],  # Num residues
            # Num distinct fftype for atom, bond, angle, dihedral
            bond_fftype_num=block[15],
            angle_fftype_num=block[16],
            dihedral_fftype_num=block[17],
            atom_fftype_num=block[18],
            # Misc
            box_kind=BoxKind.from_prmtop_idx(block[27]),
            resids_max_atoms_num=block[28],
            solv_cap_kind=SolvCapKind.from_prmtop_idx(block[29]),
            extra_points_num=block[30],
            # Path Integral MD (PIMD) slices, optional
            pimd_slices_num=block[31] if len(block) == 32 else None,
        )


class _Accessor:
    r"""
    Indirectly manage properties of a Prmtop
    """

    def __init__(self, prmtop: "Prmtop") -> None:
        self._prmtop = prmtop


class _InteractionAccessor(_Accessor):
    r"""
    Manage FF interactions in a prmtop. All interactions must have a
    "force_const" property
    """

    # Interaction blocks are reshaped if they are more natural in a different shape
    prefix: tp.ClassVar[str] = ""
    shape: tp.ClassVar[tp.Tuple[int, ...]] = (-1,)

    def num(self, kind: tp.Literal["with-H", "without-H", "all"]) -> int:
        if kind == "with-H":
            return (
                self._prmtop.blocks.get(
                    Flag[f"{self.prefix}_WITH_HYDROGEN"], np.array([])
                )
                .reshape(self.shape)
                .shape[0]
            )
        if kind == "without-H":
            return (
                self._prmtop.blocks.get(
                    Flag[f"{self.prefix}_WITHOUT_HYDROGEN"], np.array([])
                )
                .reshape(self.shape)
                .shape[0]
            )
        if kind == "all":
            return self.num("with-H") + self.num("without-H")
        raise ValueError("Kind should be one of 'with-H', 'without-H', 'all'")

    @property
    def fftype_num(self) -> int:
        return self.fftype_force_const.shape[0]

    @property
    def fftype_force_const(self) -> NDArray[np.float32]:
        return self._prmtop.blocks[Flag[f"{self.prefix}_FFTYPE_FORCE_CONSTANT"]]


class BondsAccessor(_InteractionAccessor):
    prefix: tp.ClassVar[str] = "BOND"
    shape: tp.ClassVar[tp.Tuple[int, ...]] = (-1, 3)  # i, j, idx-into-param-array

    @property
    def fftype_equil_distance(self) -> NDArray[np.float32]:
        return self._prmtop.blocks[Flag.BOND_FFTYPE_EQUIL_DISTANCE]


class AnglesAccessor(_InteractionAccessor):
    prefix: tp.ClassVar[str] = "ANGLE"
    shape: tp.ClassVar[tp.Tuple[int, ...]] = (-1, 4)  # i, j, k, idx-into-param-array

    @property
    def fftype_equil_angle(self) -> NDArray[np.float32]:
        return self._prmtop.blocks[Flag.ANGLE_FFTYPE_EQUIL_ANGLE]


class DihedralsAccessor(_InteractionAccessor):
    r"""
    Its important to first index into periodicity array, if that value is
    negative then the next value is also associated with the same set of atoms
    (it is a multi-term dihedral)

    'fftype_num' counts dihedrals that apply to the same atoms as different terms
    'fftype_group_num' groups those dihedrals in the same term
    """

    prefix: tp.ClassVar[str] = "DIHEDRAL"
    shape: tp.ClassVar[tp.Tuple[int, ...]] = (-1, 5)  # i, j, k, l, idx-into-param-array

    @property
    def fftype_group_num(self) -> int:
        is_group_end = self._prmtop.blocks[Flag.DIHEDRAL_FFTYPE_PERIODICITY] >= 0.0
        return np.sum(is_group_end).item()

    @property
    def fftype_periodicity(self) -> NDArray[np.float32]:
        return self._prmtop.blocks[Flag.DIHEDRAL_FFTYPE_PERIODICITY]

    @property
    def fftype_phase(self) -> NDArray[np.float32]:
        return self._prmtop.blocks[Flag.DIHEDRAL_FFTYPE_PHASE]

    # The "ends" of a dihedral are atoms 1-4
    # TODO its not clear if this is directly (half_barrier / damp)
    # Weiner, et al., JACS 106:765 (1984) p. 769
    # in the (half_barrier / damp) * (1 + cos(periodicity * phi - phase))
    # equation used in the terms
    @property
    def fftype_ends_electro_screen(self) -> NDArray[np.float32]:
        return self._prmtop.blocks[Flag.DIHEDRAL_FFTYPE_ELECTRO_ENDS_SCREEN]

    @property
    def fftype_ends_lj_screen(self) -> NDArray[np.float32]:
        return self._prmtop.blocks[Flag.DIHEDRAL_FFTYPE_LJ_ENDS_SCREEN]


class SoltSolvAccessor(_Accessor):
    r"""
    Manage SoltSolv properties of a Prmtop
    """

    @property
    def num(self) -> int:
        return 2

    # Not standard in amber, thus, non-settable by default
    # Num of molecules in the solvent may be 0
    @property
    def label(self) -> NDArray[np.str_]:
        return np.arange(["SOLUTE", "SOLVENT"], dtype=np.str_)

    @property
    def molecs_num(self) -> NDArray[np.int64]:
        r"""
        Number of molecs in solt and solv
        """
        solt_molec_num = self._prmtop.blocks[Flag.SOLVENT_POINTERS][-1] - 1
        return np.array(
            [solt_molec_num, self._prmtop.molecs.num - solt_molec_num], dtype=np.int64
        )

    @property
    def max_molecs_num(self) -> int:
        return np.max(self.molecs_num).item()


class MoleculesAccessor(_Accessor):
    r"""
    Manage molecs properties of a Prmtop
    """

    # Molecules consitute sequential ranges over the residues
    @property
    def num(self) -> int:
        return self._prmtop.blocks[Flag.ATOMS_PER_MOLECULE].shape[0]

    # Not standard in amber, thus, non-settable by default
    @property
    def label(self) -> NDArray[np.str_]:
        r"""
        Labels associated with the molecs

        Mono-resid molecs are given a label equal to the residue. Poly-resid
        molecs are given a standard ``POLYRESID_MOLEC_<num>`` label.
        """
        labels = []
        cumu_resid_num = 0
        for j, s in enumerate(self.resids_num):
            cumu_resid_num += s
            if s == 1:
                labels.append(self._prmtop.resids.label[cumu_resid_num])
            else:
                labels.append(f"POLYRESID_MOLEC_{j}")
        return np.array([labels], dtype=np.str_)

    # Not enforced in prmtop, but required
    @property
    def resids_num(self) -> NDArray[np.int64]:
        r"""
        Number of resids in each molecule
        """
        resid_iter = iter(self._prmtop.resids.atoms_num)
        resid_nums = []
        for size in self.atoms_num:
            resid_num = 0
            cumu_size = 0
            while cumu_size < size:
                cumu_size += next(resid_iter)
                resid_num += 1
            if cumu_size != size:
                raise RuntimeError("Inconsistency found in prmtop resids")
            resid_nums.append(resid_num)
        # Sum of the resid nums must be equal to resids.num
        return np.array(resid_nums, dtype=np.int64)

    @property
    def atoms_num(self) -> NDArray[np.int64]:
        r"""
        Number of atoms in each molecule
        """
        return self._prmtop.blocks[Flag.ATOMS_PER_MOLECULE]

    @property
    def max_resids_num(self) -> int:
        return np.max(self.resids_num).item()

    @property
    def max_atoms_num(self) -> int:
        return np.max(self.atoms_num).item()


class ResiduesAccessor(_Accessor):
    r"""
    Manage resids properties of a Prmtop
    """

    # Residues consitute sequential ranges over the atoms
    @property
    def num(self) -> int:
        return self._prmtop.blocks[Flag.RESIDUE_LABEL].shape[0]

    @property
    def label(self) -> NDArray[np.str_]:
        return self._prmtop.blocks[Flag.RESIDUE_LABEL]

    @property
    def atoms_num(self) -> NDArray[np.int64]:
        # Sum of the resids sizes must be equal to atoms.num
        starting_atom_index = np.append(
            self._prmtop.blocks[Flag.RESIDUE_FIRST_ATOM_IDX1] - 1,
            [self._prmtop.atoms.num],
        )
        return np.diff(starting_atom_index)

    @property
    def max_atoms_num(self) -> int:
        return np.max(self.atoms_num).item()


class AtomsAccessor(_Accessor):
    r"""
    Manage atom properties of a Prmtop
    """

    @property
    def num(self) -> int:
        return self.znum.shape[0]

    @property
    def znum(self) -> NDArray[np.int64]:
        return self._prmtop.blocks[Flag.ATOM_ZNUM]

    @property
    def label(self) -> NDArray[np.str_]:
        return self._prmtop.blocks[Flag.ATOM_LABEL]

    @property
    def polarizability(self) -> tp.Optional[NDArray[np.float32]]:
        return self._prmtop.blocks.get(Flag.ATOM_POLARIZABILITY, None)

    @property
    def charge(self) -> NDArray[np.float32]:
        return self._prmtop.blocks[Flag.ATOM_CHARGE] * AMBER_ATOM_CHARGE_SCALE_FACTOR

    @property
    def charge_amber_units(self) -> NDArray[np.float32]:
        return self._prmtop.blocks[Flag.ATOM_CHARGE]

    @property
    def mass(self) -> NDArray[np.float32]:
        return self._prmtop.blocks[Flag.ATOM_MASS]

    @property
    def implsv_radii(self) -> NDArray[np.float32]:
        return self._prmtop.blocks[Flag.ATOM_IMPLSV_RADII]

    @property
    def implsv_screen(self) -> NDArray[np.float32]:
        return self._prmtop.blocks[Flag.ATOM_IMPLSV_SCREEN]

    # The fftype is given by a str
    @property
    def fftype(self) -> NDArray[np.str_]:
        return self._prmtop.blocks[Flag.ATOM_FFTYPE]

    @property
    def fftype_num(self) -> int:
        return np.unique(self.fftype).shape[0]

    # The ljindex is given by an idx, which idxs into the ljindex array
    @property
    def ljindex(self) -> NDArray[np.int64]:
        return self._prmtop.blocks[Flag.ATOM_LJINDEX]

    @property
    def ljindex_num(self) -> int:
        return int(math.sqrt(self.ljindex_square))

    @property
    def ljindex_square(self) -> int:
        return self._prmtop.blocks[Flag.LJ_PARAM_INDEX].shape[0]

    # Legacy and dummy auto-generated properties
    @property
    def legacy_graph_label(self) -> NDArray[np.str_]:
        # possible values:
        # - main: '   M'
        # - side: '   S'
        # - branch-into-2: '   B'
        # - branch-into-3: '   3'
        # - end: '   E'
        # - blah: ' BLA' placeholder value that also seems to be allowed
        block = self._prmtop.blocks.get(Flag.ATOM_LEGACY_GRAPH_LABEL, None)
        if block is not None:
            return block
        return np.array(["BLA"] * self.num, dtype=np.str_)

    @property
    def legacy_graph_join_idx(self) -> NDArray[np.int64]:
        return np.zeros(self.num, dtype=np.int64)

    @property
    def legacy_rotation_idx(self) -> NDArray[np.int64]:
        return np.zeros(self.num, dtype=np.int64)

    @property
    def fftype_legacy_solty(self) -> NDArray[np.float32]:
        return np.zeros(self.fftype_num, dtype=np.float32)


@dataclass
class Prmtop:
    date_time: tp.Optional[str] = None
    name: str = "default_name"
    version: str = "V0001.000"
    blocks: tp.Dict[Flag, NDArray[tp.Any]] = field(default_factory=dict)
    box_kind: BoxKind = BoxKind.NO_BOX
    solv_cap_kind: SolvCapKind = SolvCapKind.NO_SOLV_CAP
    cmap_param_comments: tp.Dict[Flag, str] = field(default_factory=dict)
    pimd_slices_num: tp.Optional[int] = None

    def __post_init__(self) -> None:
        self.atoms = AtomsAccessor(self)

        # Partitions of the atoms seq
        self.resids = ResiduesAccessor(self)  # Partition of the atoms seq
        self.molecs = MoleculesAccessor(self)  # Partition of the resids seq
        self.solt_solv = SoltSolvAccessor(self)  # Partition of the molecs seq

        # Bonded Interactions
        self.bonds = BondsAccessor(self)
        self.angles = AnglesAccessor(self)
        self.dihedrals = DihedralsAccessor(self)

    @property
    def excluded_atoms_num(self) -> int:
        return self.blocks[Flag.EXCLUDED_ATOMS_LIST].shape[0]

    @property
    def polarizable_params_kind(self) -> PolarizableKind:
        if Flag.DIPOLE_DAMP in self.blocks:
            return PolarizableKind.POLARIZABILITY_AND_DIPOLE_DAMP
        elif Flag.ATOM_POLARIZABILITY in self.blocks:
            return PolarizableKind.POLARIZABILITY
        return PolarizableKind.NONE

    @property
    def extra_points_num(self) -> int:
        return np.sum(self.blocks[Flag.ATOM_FFTYPE] == "EP  ").item()

    # Boolean flags
    @property
    def has_extra_points(self) -> bool:
        return self.extra_points_num > 0

    @property
    def has_c4_params(self) -> bool:
        return Flag.LJ_PARAM_C in self.blocks

    @property
    def has_box(self) -> bool:
        return self.box_kind is not BoxKind.NO_BOX

    @property
    def has_solv_cap(self) -> bool:
        return self.solv_cap_kind is not SolvCapKind.NO_SOLV_CAP

    @property
    def has_cmap(self) -> bool:
        return Flag.CMAP_COUNT in self.blocks

    @classmethod
    def dummy_from_znums(
        cls,
        znums: tp.Sequence[int],
        name: str = "dummy",
        date_time: tp.Optional[str] = None,
    ) -> tpx.Self:
        _znums = np.array(znums, dtype=np.int64)
        blocks: tp.Dict[Flag, NDArray[tp.Any]] = {}
        blocks[Flag.ATOM_LABEL] = np.array(
            [f"{PERIODIC_TABLE[z]}".ljust(4) for z in _znums], dtype=np.str_
        )
        blocks[Flag.ATOM_CHARGE] = np.zeros(len(_znums), dtype=np.float32)
        blocks[Flag.ATOM_ZNUM] = _znums
        # Try first ff19SB mass, and if that doesn't work fall back to scipy
        blocks[Flag.ATOM_MASS] = np.array(
            [
                FF19SB_ATOMIC_MASS.get(
                    PERIODIC_TABLE[z], ATOMIC_MASS[PERIODIC_TABLE[z]]
                )
                for z in _znums
            ],
            dtype=np.float32,
        )
        blocks[Flag.ATOM_LJINDEX] = np.ones(len(_znums), dtype=np.int64)
        # NOTE I never see zeros in amber, which is suspicious, not sure if valid
        blocks[Flag.NUMBER_EXCLUDED_ATOMS] = np.zeros(len(_znums), dtype=np.int64)
        # NOTE Not sure if the following is valid, LJ indexing in Amber is confusing
        blocks[Flag.LJ_PARAM_INDEX] = np.array([1], dtype=np.int64)
        blocks[Flag.RESIDUE_LABEL] = np.array(
            ["BLA"] * len(_znums),
            dtype=np.str_,
        )
        blocks[Flag.RESIDUE_FIRST_ATOM_IDX1] = np.arange(
            1,
            len(_znums) + 1,
            dtype=np.int64,
        )
        # BOND, ANGLE, DIHEDRAL FFTYPE (empty)
        # These lj params seem logical placeholders
        blocks[Flag.LJ_PARAM_A] = np.array([2.0], dtype=np.float32)
        blocks[Flag.LJ_PARAM_B] = np.array([0.1], dtype=np.float32)
        # BONDS|ANGLES|DIHEDRALS_with(out)_... (check if possible to make empty)
        blocks[Flag.BOND_FFTYPE_FORCE_CONSTANT] = np.array([1.0], dtype=np.float32)
        blocks[Flag.BOND_FFTYPE_EQUIL_DISTANCE] = np.array([1.0], dtype=np.float32)
        blocks[Flag.ANGLE_FFTYPE_FORCE_CONSTANT] = np.array([1.0], dtype=np.float32)
        blocks[Flag.ANGLE_FFTYPE_EQUIL_ANGLE] = np.array([90.0], dtype=np.float32)
        blocks[Flag.DIHEDRAL_FFTYPE_FORCE_CONSTANT] = np.array([0.0], dtype=np.float32)
        blocks[Flag.DIHEDRAL_FFTYPE_PERIODICITY] = np.array([1.0], dtype=np.float32)
        blocks[Flag.DIHEDRAL_FFTYPE_PHASE] = np.array([0.0], dtype=np.float32)
        # 1.2 and 0 are std placeholder values for these in Amber
        blocks[Flag.DIHEDRAL_FFTYPE_ELECTRO_ENDS_SCREEN] = np.array(
            [1.2], dtype=np.float32
        )
        blocks[Flag.DIHEDRAL_FFTYPE_LJ_ENDS_SCREEN] = np.array([2.0], dtype=np.float32)
        # NOTE Not sure if the following is valid, also I sometimes see zeros
        # here, which is strange
        blocks[Flag.EXCLUDED_ATOMS_LIST] = np.array([], dtype=np.int64)
        blocks[Flag.ATOM_FFTYPE] = np.array(["TP"] * len(_znums), dtype=np.str_)
        # NOTE not sure if this is valid
        blocks[Flag.SOLVENT_POINTERS] = np.array(
            [len(_znums), len(_znums), len(_znums) + 1], dtype=np.int64
        )
        blocks[Flag.ATOMS_PER_MOLECULE] = np.ones(len(_znums), dtype=np.int64)
        blocks[Flag.RADIUS_SET] = np.array(["Dummy radii"], dtype=np.str_)
        blocks[Flag.ATOM_IMPLSV_RADII] = np.ones(len(_znums), dtype=np.float32)
        blocks[Flag.ATOM_IMPLSV_SCREEN] = np.ones(len(_znums), dtype=np.float32)
        return cls(
            name=name,
            date_time=date_time,
            blocks=blocks,
        )

    @classmethod
    def load(cls, path: Path) -> tpx.Self:
        r"""Construct from blocks in an Amber '*.prmtop' file"""
        blocks: tp.Dict[Flag, NDArray[tp.Any]] = {}
        cmap_param_comments: tp.Dict[Flag, str] = {}
        with open(path, mode="r", encoding="utf-8") as f:
            raw_blocks: tp.Dict[Flag, tp.List[tp.Any]] = defaultdict(list)
            flag = Flag.NAME
            fmt = Format.STRING
            for line in f:
                if line.startswith("%COMMENT") and flag.value.startswith(
                    "CMAP_PARAMETER"
                ):
                    cmap_param_comments[flag] = line[10:].strip()
                if (
                    not line
                    or line.startswith("%COMMENT")
                    or line.startswith("%VERSION")
                ):
                    continue
                elif line.startswith("%FLAG"):
                    flag = Flag(line.split()[-1])
                elif line.startswith("%FORMAT"):
                    if flag is Flag.NAME:
                        # Override this format since it is incorrectly written in
                        # the prmtops
                        fmt = Format.STRING
                    else:
                        fmt_string = line.split("(")[-1].replace(")", "").strip()
                        fmt = Format(fmt_string.upper())
                else:
                    if flag is Flag.POINTERS:
                        continue
                    raw_blocks[flag].extend(_read_line_with_format(line, fmt))

            blocks = {flag: np.asarray(list_) for flag, list_ in raw_blocks.items()}

        _remove_legacy_blocks(blocks)
        name: str = blocks.pop(Flag.NAME)[0]
        meta = PrmtopMeta.load(path)
        obj = cls(
            name=name,
            blocks=blocks,
            cmap_param_comments=cmap_param_comments,
            # Fill from PrmtopMeta
            solv_cap_kind=meta.solv_cap_kind,  # Redundant
            version=meta.version,  # Only in TITLE
            date_time=meta.date_time,  # Only in TITLE
            box_kind=meta.box_kind,  # Only in POINTERS
            pimd_slices_num=meta.pimd_slices_num,  # Only in POINTERS
        )
        # TODO check internal consistency with box, solv-cap and polarizability
        obj.check_meta_consistency(meta)
        return obj

    def check_meta_consistency(self, meta: PrmtopMeta) -> None:
        if (
            self.version != meta.version
            or self.date_time != meta.date_time
            or self.atoms.ljindex_num != meta.atom_ljindex_num
            or self.bonds.num("with-H") != meta.bond_with_hydrogen_num
            or self.bonds.num("without-H") != meta.bond_without_hydrogen_num
            or self.angles.num("with-H") != meta.angle_with_hydrogen_num
            or self.angles.num("without-H") != meta.angle_without_hydrogen_num
            or self.dihedrals.num("with-H") != meta.dihedral_with_hydrogen_num
            or self.dihedrals.num("without-H") != meta.dihedral_without_hydrogen_num
            or self.atoms.fftype_num != meta.atom_fftype_num
            or self.bonds.fftype_num != meta.bond_fftype_num
            or self.angles.fftype_num != meta.angle_fftype_num
            or self.dihedrals.fftype_num != meta.dihedral_fftype_num
            or self.atoms.num != meta.atoms_num
            or self.resids.num != meta.resids_num
            or self.resids.max_atoms_num != meta.resids_max_atoms_num
            or self.excluded_atoms_num != meta.excluded_atoms_num
            or self.pimd_slices_num != meta.pimd_slices_num
            or self.extra_points_num != meta.extra_points_num
            or self.solv_cap_kind != meta.solv_cap_kind
            or self.box_kind != meta.box_kind
        ):
            raise PrmtopError("Prmtop is inconsistent with metadata")

    def _create_raw_pointers_block(
        self,
    ) -> NDArray[np.int64]:
        pointers: tp.List[int] = [
            self.atoms.num,
            self.atoms.ljindex_num,
            self.bonds.num("with-H"),
            self.bonds.num("without-H"),
            self.angles.num("with-H"),
            self.angles.num("without-H"),
            self.dihedrals.num("with-H"),
            self.dihedrals.num("without-H"),
            0,  # Unused
            0,  # Addless format, not supported
            self.excluded_atoms_num,
            self.resids.num,
            # The following 3 include "constraints", but those are not supported
            self.bonds.num("without-H"),
            self.angles.num("without-H"),
            self.dihedrals.num("without-H"),
            # Distinct fftype for atom, bond, angle, dihedral
            self.bonds.fftype_num,
            self.angles.fftype_num,
            self.dihedrals.fftype_num,
            self.atoms.fftype_num,
            0,  # 10-12 pair fftype num, not supported
        ]
        pointers.extend([0] * 7)  # Perturbation info, not supported
        pointers.extend(
            [
                self.box_kind.prmtop_idx,
                self.resids.max_atoms_num,
                self.solv_cap_kind.prmtop_idx,
                self.extra_points_num,
            ]
        )
        if self.pimd_slices_num is not None:
            pointers.append(self.pimd_slices_num)
        return np.array(pointers, dtype=np.int64)

    def dump(
        self,
        path: Path,
        write_new_date: bool = True,
    ) -> None:
        r"""
        The block order and CMAP_PARAMETER comments are preserved
        """
        open(path, "w").close()  # truncate
        _write_version_and_datetime(
            path,
            self.version,
            date_time=None if write_new_date else self.date_time,
        )
        # The flag specifies the format in whih the appended block is written
        for flag in list(Flag):
            # These special flags don't come from blocks
            if flag is Flag.NAME:
                self._append_block(np.array([self.name]), path, flag)
            elif flag is Flag.POINTERS:
                self._append_block(self._create_raw_pointers_block(), path, flag)
            elif flag is Flag.IPOL:
                self._append_block(
                    np.array([self.polarizable_params_kind.prmtop_idx]),
                    path,
                    Flag.IPOL,
                )

            # Unused legacy blocks that must be present
            elif flag is Flag.ATOM_FFTYPE_LEGACY_SOLTY:
                self._append_block(self.atoms.fftype_legacy_solty, path, flag)
            elif flag is Flag.ATOM_LEGACY_GRAPH_JOIN_IDX:
                self._append_block(self.atoms.legacy_graph_join_idx, path, flag)
            elif flag is Flag.ATOM_LEGACY_ROTATION_IDX:
                self._append_block(self.atoms.legacy_rotation_idx, path, flag)
            elif flag is Flag.ATOM_LEGACY_GRAPH_LABEL:
                self._append_block(self.atoms.legacy_graph_label, path, flag)

            # Optional flags can be fully ommitted
            elif flag in OPTIONAL_FLAGS:
                if flag in self.blocks:
                    if flag.value.startswith("CMAP_PARAMETER"):
                        comment = self.cmap_param_comments.get(flag, None)
                    else:
                        comment = None
                    self._append_block(self.blocks[flag], path, flag, comment=comment)

            # All other flags must exist, but may be empty
            else:
                # TODO: double check which are actually required
                self._append_block(self.blocks.get(flag, np.array([])), path, flag)

    @staticmethod
    def _append_block(
        data: tp.Iterable[tp.Any],
        path: Path,
        flag: Flag,
        comment: tp.Optional[str] = None,
    ) -> None:
        with open(path, mode="a", encoding="utf-8") as f:
            # Left justification and padding needed to pedantically match leap
            f.write("".join((f"%FLAG {flag.value}".ljust(80), "\n")))
            if comment is not None:
                f.write("".join((f"%COMMENT  {comment}".ljust(80), "\n")))
            # Replace uppercase format with lowercase to pedantically match leap
            fmt_str = FLAG_FORMAT_MAP[flag].value
            fmt_str = fmt_str.replace("20A4", "20a4").replace("1A80", "1a80")
            f.write("".join((f"%FORMAT({fmt_str})".ljust(80), "\n")))
            fmt = FLAG_FORMAT_MAP[flag]
            if fmt in LARGE_INTEGER_FORMATS:
                num_per_line = 10
                width = 8
                specifier = "d"
                decimals = ""
                align = ">"
            elif fmt is Format.CMAP_FLOAT_ARRAY:
                num_per_line = 8
                width = 9
                decimals = ".5"
                specifier = "f"
                align = ">"
            elif fmt is Format.SMALL_INT_ARRAY:
                num_per_line = 20
                width = 4
                specifier = "d"
                decimals = ""
                align = ">"
            elif fmt in LARGE_FLOAT_FORMATS:
                num_per_line = 5
                width = 16
                specifier = "E"
                decimals = ".8"
                align = ">"
            elif fmt is Format.SMALL_STRING_ARRAY:
                num_per_line = 20
                width = 4
                specifier = "s"
                decimals = ""
                align = "<"
            elif (fmt is Format.STRING) or (flag is Flag.NAME):
                num_per_line = 1
                width = 80
                specifier = "s"
                decimals = ""
                align = "<"
            line = [format(i, f"{align}{width}{decimals}{specifier}") for i in data]
            if len(line) % num_per_line:
                extra_data = (num_per_line - len(line) % num_per_line) * [" " * width]
                line.extend(extra_data)
            array: NDArray[np.str_] = np.array(line, dtype=np.str_).reshape(
                -1, num_per_line
            )
            for j, row in enumerate(array):
                str_line = "".join(row)
                if j == array.shape[0] - 1:
                    str_line = str_line.rstrip()
                    if fmt is Format.SMALL_STRING_ARRAY and len(str_line) % 4:
                        # Reintroduce right pad
                        str_line = "".join((str_line, " " * (4 - len(str_line) % 4)))
                    # Reproduce leap quirks
                    elif fmt is Format.STRING or flag in (Flag.CMAP_COUNT, Flag.NAME):
                        str_line = str_line.ljust(80)
                f.write("".join((str_line, "\n")))

            # Empty block
            if array.shape[0] == 0:
                f.write("\n")


def _remove_legacy_blocks(blocks: tp.Dict[Flag, NDArray[tp.Any]]) -> None:
    # Unused, if present must be filled with zeros
    for flag in (
        Flag.ATOM_FFTYPE_LEGACY_SOLTY,
        Flag.ATOM_LEGACY_GRAPH_JOIN_IDX,
        Flag.ATOM_LEGACY_ROTATION_IDX,
    ):
        if flag in blocks:
            block = blocks.pop(flag)
            if (block != 0).any():
                raise RuntimeError(f"All values in the {flag.value} block should be 0")

    # Unused or redundant
    blocks.pop(Flag.IPOL, None)
    for flag in HBOND_FLAGS:
        blocks.pop(flag, None)


def load_single_raw_prmtop_block(prmtop: Path, flag: Flag) -> tp.List[tp.Any]:
    r"""
    Read a single prmtop "block", as determined by a given Flag, with no parsing

    Prmtop information is separated into blocks, which are delimited by "flags"
    Read one of these in a raw format and don't perform any extra post-processing.
    """
    in_block = False
    block = []
    with open(prmtop, mode="r", encoding="utf-8") as f:
        for line in f:
            if (
                not line
                or line.startswith("%COMMENT")
                or line.startswith("%VERSION")
                or line.startswith("%FORMAT")
            ):
                continue
            elif line.startswith("%FLAG"):
                current_flag = Flag(line.split()[-1])
                if current_flag is not flag:
                    if in_block:
                        break
                    else:
                        continue
                else:
                    in_block = True
            elif in_block:
                block.extend(_read_line_with_format(line, FLAG_FORMAT_MAP[flag]))
        return block


def _read_line_with_format(line: str, format_: Format) -> tp.List[tp.Any]:
    line = line[:-1].rstrip()
    parsed_line: tp.List[tp.Any] = []
    if not line:
        return parsed_line

    if format_ in LARGE_INTEGER_FORMATS:
        # Avoid flake8 warnings for slice operator
        parsed_line = [int(line[i : i + 8]) for i in range(0, len(line), 8)]  # noqa
    elif format_ is Format.SMALL_INT_ARRAY:
        parsed_line = [int(line[i : i + 4]) for i in range(0, len(line), 4)]  # noqa
    elif format_ is Format.CMAP_FLOAT_ARRAY:
        parsed_line = [float(line[i : i + 9]) for i in range(0, len(line), 9)]  # noqa
    elif format_ in LARGE_FLOAT_FORMATS:
        parsed_line = [float(line[i : i + 16]) for i in range(0, len(line), 16)]  # noqa
    elif format_ is Format.SMALL_STRING_ARRAY:
        if len(line) % 4:
            line = "".join((line, " " * (4 - len(line) % 4)))  # reintroduce right pad
        parsed_line = [line[i : i + 4] for i in range(0, len(line), 4)]  # noqa
    elif format_ is Format.STRING:
        parsed_line = [line]
    return parsed_line


def _write_version_and_datetime(
    prmtop: Path,
    version: str,
    date_time: tp.Optional[str] = None,
) -> None:
    if date_time is None:
        date_time = datetime.datetime.today().strftime("%m/%d/%y  %H:%M:%S")
    with open(prmtop, "a", encoding="utf-8") as f:
        f.write(
            "".join(
                (
                    f"%VERSION  VERSION_STAMP = {version}  DATE = {date_time}".ljust(
                        80
                    ),
                    "\n",
                )
            )
        )
