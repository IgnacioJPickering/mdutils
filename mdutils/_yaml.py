from messtamer import register_yaml_enum
from mdutils.amber.prmtop_blocks import Format, Flag
from mdutils.ani import ModelKind, AniNeighborlistKind
from mdutils.backends import DynamicsBackend
from mdutils.barostats import Barostat, Scaling
from mdutils.box import BoxKind
from mdutils.hmr import HMR
from mdutils.optimizers import Optimizer
from mdutils.init import InitialVelocities
from mdutils.options import Step, Ensemble
from mdutils.solvent import SolventModel
from mdutils.surface_tensionstats import Plane
from mdutils.thermostats import Thermostat
from mdutils.ff import WaterFF, GeneralFF, ProteinFF

register_yaml_enum(Format)
register_yaml_enum(Flag)
register_yaml_enum(ModelKind)
register_yaml_enum(AniNeighborlistKind)
register_yaml_enum(DynamicsBackend)
register_yaml_enum(Barostat)
register_yaml_enum(Scaling)
register_yaml_enum(BoxKind)
register_yaml_enum(HMR)
register_yaml_enum(Optimizer)
register_yaml_enum(InitialVelocities)
register_yaml_enum(Step)
register_yaml_enum(Ensemble)
register_yaml_enum(SolventModel)
register_yaml_enum(Plane)
register_yaml_enum(Thermostat)
register_yaml_enum(WaterFF)
register_yaml_enum(GeneralFF)
register_yaml_enum(ProteinFF)
