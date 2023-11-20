from mdutils.yaml import yamlize, YamlEnum


@yamlize
class FF(YamlEnum):
    pass


@yamlize
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


@yamlize
class GeneralFF(FF):
    GAFF = "gaff"
    GAFF2 = "gaff2"


@yamlize
class ProteinFF(FF):
    FF19SB = "ff19SB"  # use with OPC (or OPC3?)
    FF14SB = "ff14SB"  # use with TIP3P
    FF14SB_ONLYSC = "ff14SBonlysc"  # only side chains version, for igb = 8 (implicit)
