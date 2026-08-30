"""Tests for battle format and regulation models."""

import pytest

from pokemon_matchup.domain.battle import BattleFormat, Regulation
from pokemon_matchup.domain.identifiers import BuildId, RegulationId


def _build_ids(count: int) -> tuple[BuildId, ...]:
    """Create distinct build identifiers for regulation tests.

    Args:
        count: Number of identifiers to create.

    Returns:
        Distinct build identifiers in a tuple.
    """
    return tuple(BuildId(f"build-{index}") for index in range(count))


def test_single_regulation_validates_team_and_selection_sizes() -> None:
    """Validate six registered builds and three selected builds for singles."""
    regulation = Regulation(
        id=RegulationId("champions-single"),
        name="Champions Single",
        battle_format=BattleFormat.SINGLE,
        team_size=6,
        selection_size=3,
        lead_size=1,
        max_mega_evolutions=1,
    )

    regulation.validate_team(_build_ids(6))
    regulation.validate_selection(_build_ids(3))


def test_double_regulation_can_use_different_selection_and_lead_sizes() -> None:
    """Represent doubles without changing the shared regulation model."""
    regulation = Regulation(
        id=RegulationId("future-double"),
        name="Future Double",
        battle_format=BattleFormat.DOUBLE,
        team_size=6,
        selection_size=4,
        lead_size=2,
        max_mega_evolutions=1,
    )

    regulation.validate_selection(_build_ids(4))
    assert regulation.lead_size == 2


def test_regulation_rejects_selection_larger_than_team() -> None:
    """Reject a selection size that exceeds the registered team size."""
    with pytest.raises(ValueError, match="selection size"):
        Regulation(
            id=RegulationId("invalid"),
            name="Invalid",
            battle_format=BattleFormat.SINGLE,
            team_size=3,
            selection_size=4,
            lead_size=1,
            max_mega_evolutions=1,
        )


def test_single_regulation_rejects_two_leads() -> None:
    """Reject a singles regulation configured with a doubles lead count."""
    with pytest.raises(ValueError, match="single battles require a lead size of 1"):
        Regulation(
            id=RegulationId("invalid-single"),
            name="Invalid Single",
            battle_format=BattleFormat.SINGLE,
            team_size=6,
            selection_size=3,
            lead_size=2,
            max_mega_evolutions=1,
        )


def test_regulation_rejects_too_many_mega_evolutions() -> None:
    """Reject a Mega Evolution limit larger than the battle selection."""
    with pytest.raises(ValueError, match="between zero and selection size"):
        Regulation(
            id=RegulationId("invalid-mega-limit"),
            name="Invalid Mega Limit",
            battle_format=BattleFormat.SINGLE,
            team_size=6,
            selection_size=3,
            lead_size=1,
            max_mega_evolutions=4,
        )


def test_regulation_rejects_wrong_team_size() -> None:
    """Reject a team whose number of builds differs from the regulation."""
    regulation = Regulation(
        id=RegulationId("champions-single"),
        name="Champions Single",
        battle_format=BattleFormat.SINGLE,
        team_size=6,
        selection_size=3,
        lead_size=1,
        max_mega_evolutions=1,
    )

    with pytest.raises(ValueError, match="exactly 6 builds"):
        regulation.validate_team(_build_ids(5))


def test_regulation_rejects_duplicate_selection() -> None:
    """Reject a selection containing the same registered build twice."""
    regulation = Regulation(
        id=RegulationId("champions-single"),
        name="Champions Single",
        battle_format=BattleFormat.SINGLE,
        team_size=6,
        selection_size=3,
        lead_size=1,
        max_mega_evolutions=1,
    )

    with pytest.raises(ValueError, match="duplicate builds"):
        regulation.validate_selection(
            (BuildId("build-1"), BuildId("build-1"), BuildId("build-2"))
        )
