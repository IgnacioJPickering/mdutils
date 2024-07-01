import pytest
from mdutils.aminoacid import (
    AMINOACIDS,
    AMINOACIDS_WITH_CO,
    CODE3_TO_LETTER_MAP,
    LETTER_TO_CODE3_MAP,
    LETTER_TO_FULLY_PROTONATED_SMILES_MAP,
)


@pytest.mark.fast
def test_aminoacids_with_co() -> None:
    assert "NME" not in AMINOACIDS_WITH_CO


@pytest.mark.fast
def test_aminoacids() -> None:
    assert AMINOACIDS[0] == "ALA"
    assert AMINOACIDS[-1] == "NME"
    assert len(LETTER_TO_CODE3_MAP) == (20 + 2)
    assert LETTER_TO_CODE3_MAP["$"] == "NME"
    assert CODE3_TO_LETTER_MAP["NME"] == "$"
    assert LETTER_TO_CODE3_MAP["A"] == "ALA"
    assert CODE3_TO_LETTER_MAP["ALA"] == "A"
    assert LETTER_TO_CODE3_MAP["^"] == "ACE"
    assert CODE3_TO_LETTER_MAP["ACE"] == "^"


@pytest.mark.fast
def test_aminoacid_smiles() -> None:
    assert LETTER_TO_FULLY_PROTONATED_SMILES_MAP["$"] == "NC"
