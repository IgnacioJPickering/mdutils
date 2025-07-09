from enum import Enum
import typing as tp
import re
import functools

import yaml

from mdutils.amber.prmtop_blocks import Format, Flag
from mdutils.dynamics import Step, Ensemble, Backend, InitVel
from mdutils.geometry import Scaling, Plane, BoxKind, NeighborlistKind
from mdutils.algorithm import ThermoKind, TensionKind, BaroKind, OptimKind
from mdutils.ff import WaterFF, GeneralFF, ProteinFF, ImplicitFF, AniFF

__all__ = ["register_yaml_enum", "yaml_load", "yaml_dump"]

_T = tp.TypeVar("_T", bound=tp.Any)

ENUM_VALUES: tp.Set[str] = set()


# Indent also "indentless" objects such as seq and dict
class _CustomDumper(yaml.SafeDumper):
    def increase_indent(self, flow: bool = False, indentless: bool = False) -> None:
        super().increase_indent(flow, False)


class _CustomLoader(yaml.SafeLoader):
    pass


# decorate enums to make them yaml-dumpable
def register_yaml_enum(cls: _T) -> _T:
    tag = f"!{cls.__name__}"
    if not issubclass(cls, Enum):
        raise ValueError("Only enums can be wrapped with register_yaml_enum")
    choices = list(m.value for m in cls)
    if ENUM_VALUES.intersection(choices):
        raise ValueError("Some members of this enum already have registered names")

    ENUM_VALUES.update(choices)
    _regex = "|".join(choices)
    regex = re.compile(f"^({_regex})$")

    def constructor(loader, node):  # type: ignore
        return cls(loader.construct_scalar(node))

    def representer(dumper, obj):  # type: ignore
        return dumper.represent_scalar(tag, obj.value)

    _CustomLoader.add_constructor(tag, constructor)
    _CustomLoader.add_implicit_resolver(tag, regex, None)
    _CustomDumper.add_representer(cls, representer)
    _CustomDumper.add_implicit_resolver(tag, regex, None)
    return cls


# Expose yaml functions
yaml_load = functools.partial(yaml.load, Loader=_CustomLoader)
yaml_dump = functools.partial(
    yaml.dump, Dumper=_CustomDumper, indent=4, allow_unicode=True, sort_keys=False
)

# Prmtop blocks
register_yaml_enum(Format)
register_yaml_enum(Flag)
# Dynamics
register_yaml_enum(Ensemble)
register_yaml_enum(Step)
register_yaml_enum(Backend)
register_yaml_enum(InitVel)
# Geometry
register_yaml_enum(NeighborlistKind)
register_yaml_enum(BoxKind)
register_yaml_enum(Plane)
register_yaml_enum(Scaling)
# Algorithms: Thermo, Baro, Tension, Optimizer
register_yaml_enum(OptimKind)
register_yaml_enum(ThermoKind)
register_yaml_enum(BaroKind)
register_yaml_enum(TensionKind)
# FF
register_yaml_enum(WaterFF)
register_yaml_enum(GeneralFF)
register_yaml_enum(ProteinFF)
register_yaml_enum(ImplicitFF)
register_yaml_enum(AniFF)
