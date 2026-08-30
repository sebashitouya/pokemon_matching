"""Static JSON implementation of the game data repository port."""

import json
from collections.abc import Mapping, Sequence
from datetime import date
from pathlib import Path

from pokemon_matchup.domain.catalog import DataProvenance, GameDataSnapshot
from pokemon_matchup.domain.identifiers import (
    FormId,
    ItemId,
    MegaEvolutionId,
    RegulationId,
    SpeciesId,
)
from pokemon_matchup.domain.pokemon import (
    MegaEvolution,
    PokemonForm,
    PokemonSpecies,
    PokemonType,
)
from pokemon_matchup.domain.stats import BaseStats


class JsonGameDataRepository:
    """Load a versioned game data snapshot from a local JSON file."""

    def __init__(self, path: Path) -> None:
        """Initialize the repository with a snapshot path.

        Args:
            path: Local JSON snapshot to load.
        """
        self._path = path

    def load(self) -> GameDataSnapshot:
        """Load, parse, and validate the configured JSON snapshot.

        Returns:
            A validated game data snapshot.

        Raises:
            ValueError: If the JSON structure or domain data is invalid.
        """
        try:
            raw: object = json.loads(self._path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            raise ValueError(f"invalid JSON snapshot: {error.msg}") from error

        root = _as_mapping(raw, "snapshot")
        provenance = _parse_provenance(_required_mapping(root, "metadata", "snapshot"))
        species = tuple(
            _parse_species(_as_mapping(item, "species record"))
            for item in _required_sequence(root, "species", "snapshot")
        )
        forms = tuple(
            _parse_form(_as_mapping(item, "form record"))
            for item in _required_sequence(root, "forms", "snapshot")
        )
        mega_evolutions = tuple(
            _parse_mega_evolution(_as_mapping(item, "Mega Evolution record"))
            for item in _required_sequence(root, "mega_evolutions", "snapshot")
        )
        return GameDataSnapshot(provenance, species, forms, mega_evolutions)


def _parse_provenance(data: Mapping[str, object]) -> DataProvenance:
    """Parse snapshot provenance metadata.

    Args:
        data: Raw provenance mapping.

    Returns:
        Validated provenance metadata.
    """
    retrieved_on_value = _required_string(data, "retrieved_on", "metadata")
    try:
        retrieved_on = date.fromisoformat(retrieved_on_value)
    except ValueError as error:
        raise ValueError("metadata.retrieved_on must be an ISO date") from error
    return DataProvenance(
        source=_required_string(data, "source", "metadata"),
        retrieved_on=retrieved_on,
        season=_required_string(data, "season", "metadata"),
        regulation_id=RegulationId(_required_string(data, "regulation_id", "metadata")),
    )


def _parse_species(data: Mapping[str, object]) -> PokemonSpecies:
    """Parse one species record.

    Args:
        data: Raw species mapping.

    Returns:
        Validated species record.
    """
    return PokemonSpecies(
        id=SpeciesId(_required_string(data, "id", "species record")),
        name=_required_string(data, "name", "species record"),
    )


def _parse_form(data: Mapping[str, object]) -> PokemonForm:
    """Parse one form record.

    Args:
        data: Raw form mapping.

    Returns:
        Validated form record.
    """
    raw_types = _required_sequence(data, "types", "form record")
    try:
        types = tuple(
            PokemonType(_as_string(value, "form type")) for value in raw_types
        )
    except ValueError as error:
        raise ValueError(f"invalid form type: {error}") from error

    stat_data = _required_mapping(data, "base_stats", "form record")
    base_stats = BaseStats(
        hp=_required_integer(stat_data, "hp", "base_stats"),
        attack=_required_integer(stat_data, "attack", "base_stats"),
        defense=_required_integer(stat_data, "defense", "base_stats"),
        special_attack=_required_integer(stat_data, "special_attack", "base_stats"),
        special_defense=_required_integer(stat_data, "special_defense", "base_stats"),
        speed=_required_integer(stat_data, "speed", "base_stats"),
    )
    return PokemonForm(
        id=FormId(_required_string(data, "id", "form record")),
        species_id=SpeciesId(_required_string(data, "species_id", "form record")),
        name=_required_string(data, "name", "form record"),
        types=types,
        base_stats=base_stats,
    )


def _parse_mega_evolution(data: Mapping[str, object]) -> MegaEvolution:
    """Parse one Mega Evolution relationship.

    Args:
        data: Raw Mega Evolution mapping.

    Returns:
        Validated Mega Evolution relationship.
    """
    return MegaEvolution(
        id=MegaEvolutionId(_required_string(data, "id", "Mega Evolution record")),
        base_form_id=FormId(
            _required_string(data, "base_form_id", "Mega Evolution record")
        ),
        mega_form_id=FormId(
            _required_string(data, "mega_form_id", "Mega Evolution record")
        ),
        required_item_id=ItemId(
            _required_string(data, "required_item_id", "Mega Evolution record")
        ),
    )


def _required_string(data: Mapping[str, object], key: str, label: str) -> str:
    """Read a required string field from a mapping.

    Args:
        data: Mapping containing the field.
        key: Required field name.
        label: Human-readable mapping label.

    Returns:
        The string field value.
    """
    return _as_string(_required_value(data, key, label), f"{label}.{key}")


def _required_integer(data: Mapping[str, object], key: str, label: str) -> int:
    """Read a required integer field from a mapping.

    Args:
        data: Mapping containing the field.
        key: Required field name.
        label: Human-readable mapping label.

    Returns:
        The integer field value.
    """
    value = _required_value(data, key, label)
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError(f"{label}.{key} must be an integer")
    return value


def _required_mapping(
    data: Mapping[str, object], key: str, label: str
) -> Mapping[str, object]:
    """Read a required mapping field from another mapping.

    Args:
        data: Mapping containing the field.
        key: Required field name.
        label: Human-readable mapping label.

    Returns:
        The nested mapping value.
    """
    return _as_mapping(_required_value(data, key, label), f"{label}.{key}")


def _required_sequence(
    data: Mapping[str, object], key: str, label: str
) -> Sequence[object]:
    """Read a required sequence field from a mapping.

    Args:
        data: Mapping containing the field.
        key: Required field name.
        label: Human-readable mapping label.

    Returns:
        The sequence field value.
    """
    value = _required_value(data, key, label)
    if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
        raise ValueError(f"{label}.{key} must be an array")
    return value


def _required_value(data: Mapping[str, object], key: str, label: str) -> object:
    """Read a required field from a mapping.

    Args:
        data: Mapping containing the field.
        key: Required field name.
        label: Human-readable mapping label.

    Returns:
        The untyped field value.
    """
    try:
        return data[key]
    except KeyError as error:
        raise ValueError(f"{label}.{key} is required") from error


def _as_mapping(value: object, label: str) -> Mapping[str, object]:
    """Narrow an untyped value to a string-keyed mapping.

    Args:
        value: Value to narrow.
        label: Human-readable value label.

    Returns:
        The narrowed mapping.
    """
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must be an object")
    if not all(isinstance(key, str) for key in value):
        raise ValueError(f"{label} keys must be strings")
    return value


def _as_string(value: object, label: str) -> str:
    """Narrow an untyped value to a string.

    Args:
        value: Value to narrow.
        label: Human-readable value label.

    Returns:
        The narrowed string.
    """
    if not isinstance(value, str):
        raise ValueError(f"{label} must be a string")
    return value
