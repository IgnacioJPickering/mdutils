from enum import Enum

import typing_extensions as tpx


class FF(str, Enum):
    pass


class WaterFF(FF):
    TIP3P = "tip3p"
    TIP3P_FB = "tip3p-fb"
    TIP3P_FB_MOD = "tip3p-fb-mod"
    SPC_E = "spc-e"
    SPC_EB = "spc-eb"
    OPC3 = "opc3"
    POL3 = "pol3"
    SPC_FW = "spc-fw"
    Q_SPC_FW = "q-spc-fw"
    TIP4P = "tip4p"
    TIP4P_D = "tip4p-d"
    TIP4P_D_A99SB_DISP = "tip4p-d-a99sb-disp"
    TIP4P_FB = "tip4p-fb"
    TIP4P_EW = "tip4p-ew"
    OPC = "opc"
    TIP5P = "tip5p"


class GeneralFF(FF):
    GAFF = "gaff"
    GAFF2 = "gaff2"


class ProteinFF(FF):
    FF19SB = "ff19SB"  # Use with OPC (or OPC3?)
    FF14SB = "ff14SB"  # Use with TIP3P
    FF14SB_ONLY_SIDE_CHAINS = "ff14SBonlysc"  # For igb = 8 (implicit)


class AniFF(FF):
    ANI1X = "ani1x"
    ANI1CCX = "ani1ccx"
    ANI2X = "ani2x"
    ANIMBIS = "animbis"
    ANIR2S = "anir2s"
    ANIR2S_WATER = "anir2s_water"
    ANIR2S_CH3CN = "anir2s_ch3cn"
    ANIR2X_CHCL3 = "anir2s_chcl3"
    ANI2DR = "ani2dr"
    ANI2XR = "ani2xr"
    ANIALA = "aniala"
    OVERRIDE = "override"


_IMPLICIT_MDIN_IDX_MAP = {
    "gb": 1,
    "gb-mod1": 2,
    "gb-mod2": 5,
    "gbn": 7,
    "gbn-mod": 8,
    "pb": 10,
    "vacuum": 6,
}


# Implicit FF are used to model solvents in an "average" manner
class ImplicitFF(Enum):
    GB = "gb"
    MODIFIED_GB_I = "gb-mod1"
    MODIFIED_GB_II = "gb-mod2"
    GBN = "gbn"
    MODIFIED_GBN = "gbn-mod"
    POISSON_BOLTZMANN = "pb"
    VACUUM = "vacuum"

    @property
    def mdin_idx(self) -> int:
        return _IMPLICIT_MDIN_IDX_MAP[self.value]

    @classmethod
    def from_mdin_idx(cls, idx: int) -> tpx.Self:
        value = {v: k for k, v in _IMPLICIT_MDIN_IDX_MAP.items()}[idx]
        return cls(value)


_POLARIZABLE_PRMTOP_IDX_MAP = {
    "no-polarizable": 0,
    "polarizable": 1,
    "polarizable-with-dipole-damp": 2,
}


class PolarizableKind(Enum):
    NONE = "no-polarizable"
    POLARIZABILITY = "polarizable"
    POLARIZABILITY_AND_DIPOLE_DAMP = "polarizable-with-dipole-damp"

    @property
    def prmtop_idx(self) -> int:
        return _POLARIZABLE_PRMTOP_IDX_MAP[self.value]

    @classmethod
    def from_prmtop_idx(cls, idx: int) -> tpx.Self:
        value = {v: k for k, v in _POLARIZABLE_PRMTOP_IDX_MAP.items()}[idx]
        return cls(value)
