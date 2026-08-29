"""Stat, effort value, and nature models."""

from dataclasses import dataclass
from enum import StrEnum
from fractions import Fraction


class BattleStat(StrEnum):
    """A non-HP stat that can receive a nature modifier."""

    ATTACK = "attack"
    DEFENSE = "defense"
    SPECIAL_ATTACK = "special_attack"
    SPECIAL_DEFENSE = "special_defense"
    SPEED = "speed"


@dataclass(frozen=True, slots=True)
class BaseStats:
    """Base stats for a single Pokémon form."""

    hp: int
    attack: int
    defense: int
    special_attack: int
    special_defense: int
    speed: int

    def __post_init__(self) -> None:
        """Validate that every base stat is positive."""
        for name, value in self.as_dict().items():
            if value < 1:
                raise ValueError(f"{name} must be positive")

    def as_dict(self) -> dict[str, int]:
        """Return the stat values keyed by their domain names.

        Returns:
            A new mapping containing all six base stats.
        """
        return {
            "hp": self.hp,
            "attack": self.attack,
            "defense": self.defense,
            "special_attack": self.special_attack,
            "special_defense": self.special_defense,
            "speed": self.speed,
        }


@dataclass(frozen=True, slots=True)
class EffortValues:
    """Effort values assigned to a registered Pokémon build."""

    hp: int = 0
    attack: int = 0
    defense: int = 0
    special_attack: int = 0
    special_defense: int = 0
    speed: int = 0

    def __post_init__(self) -> None:
        """Validate per-stat and total effort value limits."""
        values = self.as_dict()
        for name, value in values.items():
            if not 0 <= value <= 252:
                raise ValueError(f"{name} effort value must be between 0 and 252")
        if sum(values.values()) > 510:
            raise ValueError("total effort values must not exceed 510")

    def as_dict(self) -> dict[str, int]:
        """Return the effort values keyed by their domain names.

        Returns:
            A new mapping containing all six effort values.
        """
        return {
            "hp": self.hp,
            "attack": self.attack,
            "defense": self.defense,
            "special_attack": self.special_attack,
            "special_defense": self.special_defense,
            "speed": self.speed,
        }


@dataclass(frozen=True, slots=True)
class Nature:
    """A nature and its optional increased and decreased stats."""

    name: str
    increased_stat: BattleStat | None = None
    decreased_stat: BattleStat | None = None

    def __post_init__(self) -> None:
        """Validate the name and the nature modifier pair."""
        if not self.name.strip():
            raise ValueError("nature name must not be blank")
        has_increase = self.increased_stat is not None
        has_decrease = self.decreased_stat is not None
        if has_increase != has_decrease:
            raise ValueError(
                "nature modifiers must either both be set or both be absent"
            )
        if has_increase and self.increased_stat == self.decreased_stat:
            raise ValueError("increased and decreased stats must be different")

    def modifier_for(self, stat: BattleStat) -> Fraction:
        """Return the exact nature modifier for a battle stat.

        Args:
            stat: Stat whose modifier should be returned.

        Returns:
            Eleven tenths for the increased stat, nine tenths for the decreased
            stat, and one for an unaffected stat.
        """
        if stat == self.increased_stat:
            return Fraction(11, 10)
        if stat == self.decreased_stat:
            return Fraction(9, 10)
        return Fraction(1, 1)
