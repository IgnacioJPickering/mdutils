from collections import defaultdict
import datetime
import typing as tp
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from numpy.typing import NDArray

from mdutils.box import BoxKind
from mdutils.polarizable import PolarizableKind
from mdutils.amber._prmtop_blocks import (
    Format,
    Flag,
    FLAG_FORMAT_MAP,
    LARGE_FLOAT_FORMATS,
    LARGE_INTEGER_FORMATS,
    COVALENT_TERM_FLAGS,
    HBOND_FLAGS,
    CMAP_PARAMETER_FLAGS,
)


# This is the "POINTERS" block in the prmtop file
@dataclass
class AmberPrmtopMetadata:
    atoms_num: int
    date_time: str
    version: str
    # Valence interactions with H
    bonds_with_hydrogen_num: int
    angles_with_hydrogen_num: int
    dihedrals_with_hydrogen_num: int
    # Valence interactions
    bonds_without_hydrogen_num: int
    angles_without_hydrogen_num: int
    dihedrals_without_hydrogen_num: int
    # Groups
    residues_num: int
    atom_types_num: int
    lennard_jones_atom_types_num: int
    bond_types_num: int
    angle_types_num: int
    dihedral_types_num: int
    residue_max_len: int
    excluded_atoms_num: int
    extra_points_num: int
    # Flags
    has_cap: bool
    box_kind: BoxKind
    # PIMD slices (optional)
    path_integral_md_slices_num: tp.Optional[int] = None

    @property
    def has_box(self) -> bool:
        return self.box_kind is not BoxKind.NO_BOX


@dataclass
class AmberPrmtop:
    date_time: str
    box_kind: BoxKind
    blocks: tp.Dict[Flag, NDArray[tp.Any]]
    title: str = "default_name"
    version: str = "V0001.000"
    block_order: tp.Iterable[Flag] = ()
    cmap_param_comments: tp.Optional[tp.Dict[Flag, str]] = None
    path_integral_md_slices_num: tp.Optional[int] = None

    @property
    def atoms_num(self) -> int:
        return self.blocks[Flag.ATOM_NAME].shape[0]

    @property
    def residue_sizes(self) -> NDArray[np.int_]:
        starting_atom_index = np.append(
            self.blocks[Flag.RESIDUE_POINTER] - 1,
            [self.atoms_num],
        )
        return np.diff(starting_atom_index)

    @property
    def residue_max_len(self) -> int:
        return np.max(self.residue_sizes).item()

    @property
    def excluded_atoms_num(self) -> int:
        return self.blocks[Flag.EXCLUDED_ATOMS_LIST].shape[0]

    @property
    def bonds_without_hydrogen_num(self) -> int:
        return self.blocks[Flag.BONDS_WITHOUT_HYDROGEN].shape[0]

    @property
    def bonds_with_hydrogen_num(self) -> int:
        return self.blocks[Flag.BONDS_WITH_HYDROGEN].shape[0]

    @property
    def bonds_num(self) -> int:
        return self.bonds_with_hydrogen_num + self.bonds_without_hydrogen_num

    @property
    def bond_types_num(self) -> int:
        return self.blocks[Flag.BOND_FORCE_CONSTANT].shape[0]

    @property
    def angles_without_hydrogen_num(self) -> int:
        return self.blocks[Flag.ANGLES_WITHOUT_HYDROGEN].shape[0]

    @property
    def angles_with_hydrogen_num(self) -> int:
        return self.blocks[Flag.ANGLES_WITH_HYDROGEN].shape[0]

    @property
    def angles_num(self) -> int:
        return self.angles_with_hydrogen_num + self.angles_without_hydrogen_num

    @property
    def angle_types_num(self) -> int:
        return self.blocks[Flag.ANGLE_FORCE_CONSTANT].shape[0]

    @property
    def dihedrals_without_hydrogen_num(self) -> int:
        return self.blocks[Flag.DIHEDRALS_WITHOUT_HYDROGEN].shape[0]

    @property
    def dihedrals_with_hydrogen_num(self) -> int:
        return self.blocks[Flag.DIHEDRALS_WITH_HYDROGEN].shape[0]

    @property
    def dihedrals_num(self) -> int:
        return self.dihedrals_with_hydrogen_num + self.dihedrals_without_hydrogen_num

    @property
    def dihedral_types_num(self) -> int:
        return self.blocks[Flag.DIHEDRAL_FORCE_CONSTANT].shape[0]

    @property
    def residues_num(self) -> int:
        return self.blocks[Flag.RESIDUE_LABEL].shape[0]

    @property
    def atom_types_num(self) -> int:
        return np.unique(self.blocks[Flag.AMBER_ATOM_TYPE]).shape[0]

    @property
    def lennard_jones_atom_types_num(self) -> int:
        return self.blocks[Flag.NONBONDED_PARM_INDEX].shape[0]

    @property
    def has_extra_points(self) -> bool:
        return self.extra_points_num > 0

    @property
    def extra_points_num(self) -> int:
        return np.sum(self.blocks[Flag.AMBER_ATOM_TYPE] == "EP  ").item()

    @property
    def polariable_params_kind(self) -> PolarizableKind:
        if Flag.DIPOLE_DAMP_FACTOR in self.blocks:
            return PolarizableKind.POLARIZABILITY_AND_DIPOLE_DAMP_FACTOR
        elif Flag.POLARIZABILITY in self.blocks:
            return PolarizableKind.POLARIZABILITY
        return PolarizableKind.NONE

    @property
    def has_c4_params(self) -> bool:
        return Flag.LENNARD_JONES_CCOEF in self.blocks

    @property
    def has_cap(self) -> bool:
        return Flag.CAP_INFO in self.blocks

    @property
    def has_cmap_params(self) -> bool:
        return Flag.CMAP_COUNT in self.blocks


def dump(
    data: AmberPrmtop,
    prmtop: Path,
    write_new_date: bool = True,
    preserve_block_order: bool = True,
    preserve_cmap_comments: bool = True,
) -> None:
    assert preserve_block_order, "Standard order not yet supported"
    assert preserve_cmap_comments, ""
    open(prmtop, "w").close()  # truncate
    _write_version_and_datetime(
        prmtop,
        data.version,
        date_time=None if write_new_date else data.date_time,
    )
    for flag in data.block_order:
        if flag is Flag.TITLE:
            _append_block(np.array([data.title]), prmtop, flag)
        elif flag is Flag.POINTERS:
            _append_block(_create_raw_pointers_array(data), prmtop, flag)
        elif flag in HBOND_FLAGS:
            _append_block(np.array([]), prmtop, flag)
        elif flag in COVALENT_TERM_FLAGS or (flag is Flag.NONBONDED_PARM_INDEX):
            _append_block(data.blocks[flag].reshape(-1), prmtop, flag)
        elif flag is Flag.SOLTY:
            _append_block(
                np.zeros(data.atom_types_num, dtype=np.float32), prmtop, Flag.SOLTY
            )
        # Unused legacy blocks
        elif flag is Flag.JOIN_ARRAY:
            _append_block(
                np.zeros(data.atoms_num, dtype=np.int64), prmtop, Flag.JOIN_ARRAY
            )
        elif flag is Flag.IROTAT:
            _append_block(np.zeros(data.atoms_num, dtype=np.int64), prmtop, Flag.IROTAT)
        elif flag is Flag.IPOL:
            _append_block(
                np.array([data.polariable_params_kind.value]), prmtop, Flag.IPOL
            )
        else:
            if flag in CMAP_PARAMETER_FLAGS and data.cmap_param_comments is not None:
                comment = data.cmap_param_comments[flag]
            else:
                comment = None
            _append_block(data.blocks[flag], prmtop, flag, comment=comment)


def _remove_legacy_blocks(blocks: tp.Dict[Flag, NDArray[tp.Any]]) -> None:
    # Legacy (unused)
    if Flag.SOLTY in blocks:
        if (blocks[Flag.SOLTY] != 0).any():
            raise RuntimeError(
                "Parsing error, all values in the SOLTY block should be 0"
            )
        else:
            blocks.pop(Flag.SOLTY)

    if Flag.JOIN_ARRAY in blocks:
        if (blocks[Flag.JOIN_ARRAY] != 0).any():
            raise RuntimeError(
                "Parsing error, all values in the JOIN_ARRAY block should be 0"
            )
        else:
            blocks.pop(Flag.JOIN_ARRAY)

    if Flag.IROTAT in blocks:
        if (blocks[Flag.IROTAT] != 0).any():
            raise RuntimeError(
                "Parsing error, all values in the IROTAT block should be 0"
            )
        else:
            blocks.pop(Flag.IROTAT)
    blocks.pop(Flag.IPOL, None)
    blocks.pop(Flag.HBOND_BCOEF, None)
    blocks.pop(Flag.HBOND_ACOEF, None)
    blocks.pop(Flag.HBCUT, None)


def load_single_raw_block(prmtop: Path, flag: Flag) -> tp.List[tp.Any]:
    r"""Read all info in a prmtop file"""
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


def load(prmtop: Path) -> AmberPrmtop:
    r"""Read all info in a prmtop file"""
    blocks: tp.Dict[Flag, NDArray[tp.Any]] = {}
    block_order = [Flag.TITLE]
    cmap_param_comments: tp.Dict[Flag, str] = {}
    with open(prmtop, mode="r", encoding="utf-8") as f:
        raw_blocks: tp.Dict[Flag, tp.List[tp.Any]] = defaultdict(list)
        flag = Flag.TITLE
        fmt = Format.STRING
        for line in f:
            if line.startswith("%COMMENT") and flag in CMAP_PARAMETER_FLAGS:
                cmap_param_comments[flag] = line[10:].strip()
            if not line or line.startswith("%COMMENT") or line.startswith("%VERSION"):
                continue
            elif line.startswith("%FLAG"):
                flag = Flag(line.split()[-1])
                if flag is not Flag.TITLE:
                    block_order.append(flag)
            elif line.startswith("%FORMAT"):
                if flag is Flag.TITLE:
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
        # i, j, idx
        blocks[Flag.BONDS_WITH_HYDROGEN] = blocks[Flag.BONDS_WITH_HYDROGEN].reshape(
            -1, 3
        )
        blocks[Flag.BONDS_WITHOUT_HYDROGEN] = blocks[
            Flag.BONDS_WITHOUT_HYDROGEN
        ].reshape(-1, 3)
        # i, j, k, idx
        blocks[Flag.ANGLES_WITH_HYDROGEN] = blocks[Flag.ANGLES_WITH_HYDROGEN].reshape(
            -1, 4
        )
        blocks[Flag.ANGLES_WITHOUT_HYDROGEN] = blocks[
            Flag.ANGLES_WITHOUT_HYDROGEN
        ].reshape(-1, 4)
        # i, j, k, l, idx
        blocks[Flag.DIHEDRALS_WITH_HYDROGEN] = blocks[
            Flag.DIHEDRALS_WITH_HYDROGEN
        ].reshape(-1, 5)
        blocks[Flag.DIHEDRALS_WITHOUT_HYDROGEN] = blocks[
            Flag.DIHEDRALS_WITHOUT_HYDROGEN
        ].reshape(-1, 5)
        num_nonbonded = blocks[Flag.NONBONDED_PARM_INDEX].shape[0]
        blocks[Flag.NONBONDED_PARM_INDEX] = blocks[Flag.NONBONDED_PARM_INDEX].reshape(
            int(np.sqrt(num_nonbonded)), int(np.sqrt(num_nonbonded))
        )

    _remove_legacy_blocks(blocks)
    title: str = blocks.pop(Flag.TITLE)[0]
    metadata = load_metadata(prmtop)
    return AmberPrmtop(
        title=title,
        blocks=blocks,
        block_order=block_order,
        cmap_param_comments=cmap_param_comments,
        version=metadata.version,
        date_time=metadata.date_time,
        box_kind=metadata.box_kind,
        path_integral_md_slices_num=metadata.path_integral_md_slices_num,
    )


def _append_block(
    data: tp.Iterable[tp.Any],
    prmtop: Path,
    flag: Flag,
    comment: tp.Optional[str] = None,
) -> None:
    with open(prmtop, mode="a", encoding="utf-8") as f:
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
            # -6.67300626E+00
        elif fmt is Format.SMALL_STRING_ARRAY:
            num_per_line = 20
            width = 4
            specifier = "s"
            decimals = ""
            align = "<"
        elif (fmt is Format.STRING) or (flag is Flag.TITLE):
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
                    # reintroduce right pad
                    str_line = "".join((str_line, " " * (4 - len(str_line) % 4)))
                # Reproduce leap quirks
                elif fmt is Format.STRING or flag in (Flag.CMAP_COUNT, Flag.TITLE):
                    str_line = str_line.ljust(80)
            f.write("".join((str_line, "\n")))

        # Empty block
        if array.shape[0] == 0:
            f.write("\n")


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


# The metadata is the POINTERS block, together with the title, the version and date
# Note that, if the order of the blocks is very nonstandard, there may be no speed
# advantage in loading the metadata only
def load_metadata(prmtop: Path) -> AmberPrmtopMetadata:
    version = "V0001.000"
    date_time = ""
    with open(prmtop, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("%VERSION"):
                parts = line.split()[1:]
                version = parts[2]
                date_time = f"{parts[5]}  {parts[6]}"
                break

    block = load_single_raw_block(prmtop, Flag.POINTERS)
    # Block (array) sizes and some flags
    if bool(block[20]):
        raise RuntimeError(
            "Perturbation information not supported, it should not be present"
        )
    if bool(block[8]):
        raise RuntimeError("NHPARM not supported, it should not be present")
    if bool(block[19]):
        raise RuntimeError("HBOND terms not supported, they should not be present")
    if bool(block[9]):
        raise RuntimeError(
            "Prmtops created by ADDLES not supported, flag should not be present"
        )
        # (only sander.LES accepts prmtop created by addles)
    if block[12] != block[3] or block[13] != block[5] or block[14] != block[7]:
        raise RuntimeError("Constraints not supported, they should not be present")
    # block[18] is the size of the solty array, it doesn't really matter what this is,
    # It is not used by sander/pmemd for anything. As long as the SOLTY array
    # is consistent with this size, all is good
    # (SOLTY array must exist though)
    # I will preserve it for read prmtops, but for written prmtops I will just set it
    # to 1 if the source is not a previously read prmtop.
    metadata = AmberPrmtopMetadata(
        atoms_num=block[0],
        bonds_with_hydrogen_num=block[2],
        bonds_without_hydrogen_num=block[3],
        angles_with_hydrogen_num=block[4],
        angles_without_hydrogen_num=block[5],
        dihedrals_with_hydrogen_num=block[6],
        dihedrals_without_hydrogen_num=block[7],
        excluded_atoms_num=block[10],
        residues_num=block[11],
        lennard_jones_atom_types_num=block[1],
        atom_types_num=block[18],  # Only for legacy SOLTY array
        bond_types_num=block[15],
        angle_types_num=block[16],
        dihedral_types_num=block[17],
        residue_max_len=block[28],
        extra_points_num=block[30],
        # Flags
        box_kind={
            0: BoxKind.NO_BOX,
            1: BoxKind.RECTANGULAR,
            2: BoxKind.TRUNCATED_OCTAHEDRAL,
        }[block[27]],
        has_cap=bool(block[29]),
        version=version,
        date_time=date_time,
    )
    try:
        metadata.path_integral_md_slices_num = block[31]
    except IndexError:
        pass
    return metadata


def _create_raw_pointers_array(
    data: AmberPrmtop,
) -> NDArray[np.int64]:
    pointers: tp.List[int] = [
        data.atoms_num,
        data.lennard_jones_atom_types_num,
        data.bonds_with_hydrogen_num,
        data.bonds_without_hydrogen_num,
        data.angles_with_hydrogen_num,
        data.angles_without_hydrogen_num,
        data.dihedrals_with_hydrogen_num,
        data.dihedrals_without_hydrogen_num,
        0,
        0,
        data.excluded_atoms_num,
        data.residues_num,
        data.bonds_without_hydrogen_num,
        data.angles_without_hydrogen_num,
        data.dihedrals_without_hydrogen_num,
        data.bond_types_num,
        data.angle_types_num,
        data.dihedral_types_num,
        data.atom_types_num,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        0,
        data.box_kind.value,
        data.residue_max_len,
        int(data.has_cap),
        data.extra_points_num,
    ]
    if data.path_integral_md_slices_num is not None:
        pointers.append(data.path_integral_md_slices_num)
    return np.array(pointers, dtype=np.int64)
