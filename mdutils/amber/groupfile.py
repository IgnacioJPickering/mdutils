from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape


_TEMPLATES_PATH = Path(__file__).parent.parent.joinpath("templates")


env = Environment(
    loader=FileSystemLoader(_TEMPLATES_PATH),
    autoescape=select_autoescape(),
    trim_blocks=True,
    lstrip_blocks=True,
)


def groupfile(
    name: str,
    prmtop_path: Path,
    replica_num: int = 1,
    do_remd: bool = False,
    ascii_input: bool = True,
    share_mdcrd: bool = False,
) -> str:
    renderer = env.get_template("amber.groupfile.jinja")
    return renderer.render(
        name=name,
        prmtop_path=str(prmtop_path),
        replicas=list(range(replica_num)),
        do_remd=do_remd,
        coord_suffix="inpcrd" if ascii_input else "restrt",
        share_mdcrd=share_mdcrd,
    )
