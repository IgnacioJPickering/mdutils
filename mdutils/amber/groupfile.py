import typing as tp
from pathlib import Path


def write_groupfile_block(
    prefixes: tp.Optional[tp.Sequence[str]] = None,
    temperatures_kelvin: tp.Optional[tp.Sequence[int]] = None,
    do_remd: bool = False,
    relative_to_cwd: bool = True,
    ascii_output: bool = False,
) -> str:
    if prefixes is None and temperatures_kelvin is None:
        raise ValueError(
            "At least one of 'prefixes' and 'temperatures' must be specified"
        )
    if prefixes is None:
        assert temperatures_kelvin is not None
        prefixes = [f"{t}K" for t in temperatures_kelvin]
    assert prefixes is not None
    if relative_to_cwd:
        prefixes = [f"./{p}" for p in prefixes]

    lines = []
    for i, prefix in enumerate(prefixes):
        parts = [
            "-O",
            "-rem",
            "1" if do_remd else "0",
            "-p",
            f"{prefix}/prmtop",
            "-i",
            f"{prefix}/mdin",
            "-inf",
            f"{prefix}/mdinfo",
            "-o",
            f"{prefix}/mdout",
            "-r",
            f"{prefix}/restrt",
            "-x",
            f"{prefix}/mdcrd{'' if ascii_output else '.nc'}",
            "-c",
            f"{prefix}/inpcrd",
        ]
        if do_remd:
            parts.extend(["-remlog", "rem.log"])
        if i == len(prefixes) - 1:
            parts.append("\n")
        lines.append(" ".join(parts))
    return "\n".join(lines)


def dump_groupfile(
    path: Path,
    prefixes: tp.Optional[tp.Sequence[str]] = None,
    temperatures_kelvin: tp.Optional[tp.Sequence[int]] = None,
    do_remd: bool = False,
    ascii_output: bool = False,
    relative_to_cwd: bool = True,
) -> None:
    Path(path).write_text(
        write_groupfile_block(
            prefixes,
            temperatures_kelvin,
            do_remd,
            ascii_output,
            relative_to_cwd,
        )
    )
