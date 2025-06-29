r"""
Aminoacid sequence 3-letter-codes and single-letter-codes
"""

__all__ = [
    "AMINOACIDS",
    "AMINOACIDS_WITH_CO",
    "CODE3_TO_LETTER_MAP",
    "LETTER_TO_CODE3_MAP",
    "LETTER_TO_FULLY_PROTONATED_SMILES_MAP",
]

AMINOACIDS = (
    "ALA",
    "ARG",
    "ASN",
    "ASP",
    "CYS",
    "GLU",
    "GLN",
    "GLY",
    "HIS",
    "ILE",
    "LEU",
    "LYS",
    "MET",
    "PHE",
    "PRO",
    "SER",
    "THR",
    "TRP",
    "TYR",
    "VAL",
    "ACE",
    "NME",
)

AMINOACIDS_WITH_CO = AMINOACIDS[:-1]


CODE3_TO_LETTER_MAP = {
    "ALA": "A",
    "ARG": "R",
    "ASN": "N",
    "ASP": "D",
    "CYS": "C",
    "GLU": "E",
    "GLN": "Q",
    "GLY": "G",
    "HIS": "H",
    "ILE": "I",
    "LEU": "L",
    "LYS": "K",
    "MET": "M",
    "PHE": "F",
    "PRO": "P",
    "SER": "S",
    "THR": "T",
    "TRP": "W",
    "TYR": "Y",
    "VAL": "V",
    "ACE": "^",
    "NME": "$",
}

LETTER_TO_CODE3_MAP = {v: k for k, v in CODE3_TO_LETTER_MAP.items()}

LETTER_TO_FULLY_PROTONATED_SMILES_MAP = {
    "^": "C(C=O)O",
    "A": "N[C@@]([H])(C)C(=O)O",
    "R": "N[C@@]([H])(CCCNC(=N)N)C(=O)O",
    "N": "N[C@@]([H])(CC(=O)N)C(=O)O",
    "D": "N[C@@]([H])(CC(=O)O)C(=O)O",
    "C": "N[C@@]([H])(CS)C(=O)O",
    "Q": "N[C@@]([H])(CCC(=O)N)C(=O)O",
    "E": "N[C@@]([H])(CCC(=O)O)C(=O)O",
    "G": "NCC(=O)O",
    "H": "N[C@@]([H])(CC1=CN=C-N1)C(=O)O",
    "I": "N[C@@]([H])([C@]([H])(CC)C)C(=O)O",
    "L": "N[C@@]([H])(CC(C)C)C(=O)O",
    "K": "N[C@@]([H])(CCCCN)C(=O)O",
    "M": "N[C@@]([H])(CCSC)C(=O)O",
    "F": "N[C@@]([H])(Cc1ccccc1)C(=O)O",
    "P": "N1[C@@]([H])(CCC1)C(=O)O",
    "S": "N[C@@]([H])(CO)C(=O)O",
    "T": "N[C@@]([H])([C@]([H])(O)C)C(=O)O",
    "W": "N[C@@]([H])(CC(=CN2)C1=C2C=CC=C1)C(=O)O",
    "Y": "N[C@@]([H])(Cc1ccc(O)cc1)C(=O)O",
    "V": "N[C@@]([H])(C(C)C)C(=O)O",
    "$": "NC",
}
