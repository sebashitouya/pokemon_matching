"""Tests for stat, effort value, and nature models."""

from fractions import Fraction

import pytest

from pokemon_matchup.domain.stats import (
    BaseStats,
    BattleStat,
    EffortValues,
    Nature,
)


def test_base_stats_reject_non_positive_value() -> None:
    """Reject a base stat that is not positive."""
    with pytest.raises(ValueError, match="hp must be positive"):
        BaseStats(0, 100, 100, 100, 100, 100)


def test_effort_values_accept_boundary_values() -> None:
    """Accept legal per-stat and total effort value boundaries."""
    effort_values = EffortValues(hp=252, attack=252, defense=6)

    assert sum(effort_values.as_dict().values()) == 510


@pytest.mark.parametrize("value", [-1, 253])
def test_effort_values_reject_out_of_range_value(value: int) -> None:
    """Reject a per-stat effort value outside the legal range."""
    with pytest.raises(ValueError, match="hp effort value"):
        EffortValues(hp=value)


def test_effort_values_reject_total_over_limit() -> None:
    """Reject effort values whose total exceeds the legal limit."""
    with pytest.raises(ValueError, match="must not exceed 510"):
        EffortValues(hp=252, attack=252, defense=7)


def test_nature_returns_exact_modifiers() -> None:
    """Return exact modifiers for increased, decreased, and neutral stats."""
    nature = Nature("Adamant", BattleStat.ATTACK, BattleStat.SPECIAL_ATTACK)

    assert nature.modifier_for(BattleStat.ATTACK) == Fraction(11, 10)
    assert nature.modifier_for(BattleStat.SPECIAL_ATTACK) == Fraction(9, 10)
    assert nature.modifier_for(BattleStat.SPEED) == Fraction(1, 1)


def test_neutral_nature_has_no_modified_stats() -> None:
    """Represent a neutral nature without inventing modified stats."""
    nature = Nature("Serious")

    assert nature.increased_stat is None
    assert nature.decreased_stat is None


def test_nature_rejects_incomplete_modifier_pair() -> None:
    """Reject a nature that specifies only one side of its modifiers."""
    with pytest.raises(ValueError, match="must either both be set"):
        Nature("Invalid", increased_stat=BattleStat.ATTACK)
