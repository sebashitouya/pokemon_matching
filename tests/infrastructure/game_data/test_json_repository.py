"""Tests for the static JSON game data repository."""

import json
from copy import deepcopy
from pathlib import Path

import pytest

from pokemon_matchup.application.ports.game_data_repository import (
    GameDataRepository,
)
from pokemon_matchup.domain.identifiers import FormId, SpeciesId
from pokemon_matchup.infrastructure.game_data.json_repository import (
    JsonGameDataRepository,
)


def _valid_data() -> dict[str, object]:
    """Create a valid static snapshot document.

    Returns:
        JSON-compatible snapshot data.
    """
    return {
        "metadata": {
            "source": "official-source",
            "retrieved_on": "2026-08-30",
            "season": "2026-08",
            "regulation_id": "champions-single",
        },
        "species": [{"id": "charizard", "name": "Charizard"}],
        "forms": [
            {
                "id": "charizard",
                "species_id": "charizard",
                "name": "Charizard",
                "types": ["fire", "flying"],
                "base_stats": {
                    "hp": 78,
                    "attack": 84,
                    "defense": 78,
                    "special_attack": 109,
                    "special_defense": 85,
                    "speed": 100,
                },
            },
            {
                "id": "mega-charizard-x",
                "species_id": "charizard",
                "name": "Mega Charizard X",
                "types": ["fire", "dragon"],
                "base_stats": {
                    "hp": 78,
                    "attack": 130,
                    "defense": 111,
                    "special_attack": 130,
                    "special_defense": 85,
                    "speed": 100,
                },
            },
        ],
        "mega_evolutions": [
            {
                "id": "charizard-x",
                "base_form_id": "charizard",
                "mega_form_id": "mega-charizard-x",
                "required_item_id": "charizardite-x",
            }
        ],
    }


def _write_snapshot(path: Path, data: object) -> Path:
    """Write JSON-compatible test data to a temporary path.

    Args:
        path: Destination path.
        data: JSON-compatible value to serialize.

    Returns:
        The destination path.
    """
    path.write_text(json.dumps(data), encoding="utf-8")
    return path


def test_repository_implements_game_data_port(tmp_path: Path) -> None:
    """Expose the static adapter through the application port."""
    repository = JsonGameDataRepository(
        _write_snapshot(tmp_path / "snapshot.json", _valid_data())
    )

    assert isinstance(repository, GameDataRepository)


def test_repository_loads_valid_snapshot(tmp_path: Path) -> None:
    """Load valid provenance, forms, and Mega Evolution relationships."""
    repository = JsonGameDataRepository(
        _write_snapshot(tmp_path / "snapshot.json", _valid_data())
    )

    snapshot = repository.load()

    assert snapshot.species[0].id == SpeciesId("charizard")
    assert snapshot.forms[1].id == FormId("mega-charizard-x")
    assert snapshot.mega_evolutions[0].mega_form_id == FormId("mega-charizard-x")


def test_repository_rejects_missing_provenance(tmp_path: Path) -> None:
    """Reject a snapshot without required provenance metadata."""
    data = _valid_data()
    del data["metadata"]
    repository = JsonGameDataRepository(
        _write_snapshot(tmp_path / "snapshot.json", data)
    )

    with pytest.raises(ValueError, match="snapshot.metadata is required"):
        repository.load()


def test_repository_rejects_invalid_retrieval_date(tmp_path: Path) -> None:
    """Reject provenance with a non-ISO retrieval date."""
    data = _valid_data()
    metadata = data["metadata"]
    assert isinstance(metadata, dict)
    metadata["retrieved_on"] = "August 30"
    repository = JsonGameDataRepository(
        _write_snapshot(tmp_path / "snapshot.json", data)
    )

    with pytest.raises(ValueError, match="must be an ISO date"):
        repository.load()


def test_repository_rejects_duplicate_form_id(tmp_path: Path) -> None:
    """Reject duplicate form identifiers after parsing."""
    data = _valid_data()
    forms = data["forms"]
    assert isinstance(forms, list)
    forms.append(deepcopy(forms[0]))
    repository = JsonGameDataRepository(
        _write_snapshot(tmp_path / "snapshot.json", data)
    )

    with pytest.raises(ValueError, match="form ids must be unique"):
        repository.load()


def test_repository_rejects_unknown_form_reference(tmp_path: Path) -> None:
    """Reject a Mega Evolution that references a missing form."""
    data = _valid_data()
    mega_evolutions = data["mega_evolutions"]
    assert isinstance(mega_evolutions, list)
    mega_evolution = mega_evolutions[0]
    assert isinstance(mega_evolution, dict)
    mega_evolution["mega_form_id"] = "missing-form"
    repository = JsonGameDataRepository(
        _write_snapshot(tmp_path / "snapshot.json", data)
    )

    with pytest.raises(ValueError, match="unknown Mega-Evolved form"):
        repository.load()


def test_repository_rejects_invalid_json(tmp_path: Path) -> None:
    """Reject malformed JSON with a domain-facing error."""
    path = tmp_path / "snapshot.json"
    path.write_text("{", encoding="utf-8")

    with pytest.raises(ValueError, match="invalid JSON snapshot"):
        JsonGameDataRepository(path).load()
