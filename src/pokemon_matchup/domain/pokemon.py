"""Pokémon species, form, build, and Mega Evolution models."""

from dataclasses import dataclass
from enum import StrEnum

from pokemon_matchup.domain.identifiers import (
    AbilityId,
    BuildId,
    FormId,
    ItemId,
    MegaEvolutionId,
    MoveId,
    SpeciesId,
)
from pokemon_matchup.domain.stats import BaseStats, EffortValues, Nature


class PokemonType(StrEnum):
    """A type available to a Pokémon form."""

    NORMAL = "normal"
    FIRE = "fire"
    WATER = "water"
    ELECTRIC = "electric"
    GRASS = "grass"
    ICE = "ice"
    FIGHTING = "fighting"
    POISON = "poison"
    GROUND = "ground"
    FLYING = "flying"
    PSYCHIC = "psychic"
    BUG = "bug"
    ROCK = "rock"
    GHOST = "ghost"
    DRAGON = "dragon"
    DARK = "dark"
    STEEL = "steel"
    FAIRY = "fairy"


@dataclass(frozen=True, slots=True)
class PokemonSpecies:
    """A Pokémon species shared by one or more battle forms."""

    id: SpeciesId
    name: str

    def __post_init__(self) -> None:
        """Validate required species fields."""
        _validate_identifier(self.id, "species id")
        _validate_name(self.name, "species name")


@dataclass(frozen=True, slots=True)
class PokemonForm:
    """A separately identifiable battle form of a Pokémon species."""

    id: FormId
    species_id: SpeciesId
    name: str
    types: tuple[PokemonType, ...]
    base_stats: BaseStats

    def __post_init__(self) -> None:
        """Validate identifiers, name, and typing."""
        _validate_identifier(self.id, "form id")
        _validate_identifier(self.species_id, "species id")
        _validate_name(self.name, "form name")
        if not 1 <= len(self.types) <= 2:
            raise ValueError("a form must have one or two types")
        if len(set(self.types)) != len(self.types):
            raise ValueError("a form must not repeat the same type")


@dataclass(frozen=True, slots=True)
class PokemonBuild:
    """A user-registered Pokémon build without inferred information."""

    id: BuildId
    form_id: FormId
    level: int
    nature: Nature
    effort_values: EffortValues
    move_ids: tuple[MoveId | None, ...]
    ability_id: AbilityId | None = None
    held_item_id: ItemId | None = None

    def __post_init__(self) -> None:
        """Validate identifiers, level, and move slots."""
        _validate_identifier(self.id, "build id")
        _validate_identifier(self.form_id, "form id")
        if not 1 <= self.level <= 100:
            raise ValueError("level must be between 1 and 100")
        if len(self.move_ids) != 4:
            raise ValueError("a build must contain exactly four move slots")
        known_moves = tuple(move_id for move_id in self.move_ids if move_id is not None)
        for move_id in known_moves:
            _validate_identifier(move_id, "move id")
        if len(set(known_moves)) != len(known_moves):
            raise ValueError("a build must not contain duplicate known moves")
        if self.ability_id is not None:
            _validate_identifier(self.ability_id, "ability id")
        if self.held_item_id is not None:
            _validate_identifier(self.held_item_id, "held item id")


@dataclass(frozen=True, slots=True)
class MegaEvolution:
    """A relationship between separate base and Mega-Evolved forms."""

    id: MegaEvolutionId
    base_form_id: FormId
    mega_form_id: FormId
    required_item_id: ItemId

    def __post_init__(self) -> None:
        """Validate the relationship identifiers and distinct forms."""
        _validate_identifier(self.id, "Mega Evolution id")
        _validate_identifier(self.base_form_id, "base form id")
        _validate_identifier(self.mega_form_id, "Mega-Evolved form id")
        _validate_identifier(self.required_item_id, "required item id")
        if self.base_form_id == self.mega_form_id:
            raise ValueError("base and Mega-Evolved forms must be different")


def _validate_identifier(identifier: str, label: str) -> None:
    """Validate a string-backed domain identifier.

    Args:
        identifier: Identifier value to validate.
        label: Human-readable label used in an error message.
    """
    if not identifier.strip():
        raise ValueError(f"{label} must not be blank")


def _validate_name(name: str, label: str) -> None:
    """Validate a required display name.

    Args:
        name: Display name to validate.
        label: Human-readable label used in an error message.
    """
    if not name.strip():
        raise ValueError(f"{label} must not be blank")
