"""Tests for Pokémon species, form, build, and Mega Evolution models."""

import pytest

from pokemon_matchup.domain.identifiers import (
    AbilityId,
    BuildId,
    FormId,
    ItemId,
    MegaEvolutionId,
    MoveId,
    SpeciesId,
)
from pokemon_matchup.domain.pokemon import (
    MegaEvolution,
    PokemonBuild,
    PokemonForm,
    PokemonType,
)
from pokemon_matchup.domain.stats import BaseStats, EffortValues, Nature


def test_form_accepts_two_distinct_types() -> None:
    """Represent a dual-typed form independently from its species."""
    form = PokemonForm(
        id=FormId("charizard"),
        species_id=SpeciesId("charizard"),
        name="Charizard",
        types=(PokemonType.FIRE, PokemonType.FLYING),
        base_stats=BaseStats(78, 84, 78, 109, 85, 100),
    )

    assert form.types == (PokemonType.FIRE, PokemonType.FLYING)


def test_form_rejects_duplicate_types() -> None:
    """Reject a form that repeats the same type."""
    with pytest.raises(ValueError, match="must not repeat"):
        PokemonForm(
            id=FormId("invalid"),
            species_id=SpeciesId("invalid"),
            name="Invalid",
            types=(PokemonType.FIRE, PokemonType.FIRE),
            base_stats=BaseStats(1, 1, 1, 1, 1, 1),
        )


def test_build_preserves_unknown_information() -> None:
    """Keep unknown moves, ability, and held item explicitly unknown."""
    build = PokemonBuild(
        id=BuildId("unknown-build"),
        form_id=FormId("charizard"),
        level=50,
        nature=Nature("Serious"),
        effort_values=EffortValues(),
        move_ids=(MoveId("flamethrower"), None, None, None),
    )

    assert build.move_ids[1:] == (None, None, None)
    assert build.ability_id is None
    assert build.held_item_id is None


def test_build_rejects_incorrect_move_slot_count() -> None:
    """Reject a build without exactly four move slots."""
    with pytest.raises(ValueError, match="exactly four move slots"):
        PokemonBuild(
            id=BuildId("invalid-build"),
            form_id=FormId("charizard"),
            level=50,
            nature=Nature("Serious"),
            effort_values=EffortValues(),
            move_ids=(MoveId("flamethrower"),),
        )


def test_build_rejects_duplicate_known_moves() -> None:
    """Reject duplicate known moves while allowing multiple unknown slots."""
    with pytest.raises(ValueError, match="duplicate known moves"):
        PokemonBuild(
            id=BuildId("invalid-build"),
            form_id=FormId("charizard"),
            level=50,
            nature=Nature("Serious"),
            effort_values=EffortValues(),
            move_ids=(
                MoveId("flamethrower"),
                MoveId("flamethrower"),
                None,
                None,
            ),
            ability_id=AbilityId("blaze"),
            held_item_id=ItemId("leftovers"),
        )


def test_mega_evolution_links_distinct_forms() -> None:
    """Link a base form to a separate Mega-Evolved form."""
    mega_evolution = MegaEvolution(
        id=MegaEvolutionId("charizard-x"),
        base_form_id=FormId("charizard"),
        mega_form_id=FormId("mega-charizard-x"),
        required_item_id=ItemId("charizardite-x"),
    )

    assert mega_evolution.base_form_id != mega_evolution.mega_form_id


def test_mega_evolution_rejects_same_form() -> None:
    """Reject a Mega Evolution that overwrites its base form."""
    with pytest.raises(ValueError, match="must be different"):
        MegaEvolution(
            id=MegaEvolutionId("invalid"),
            base_form_id=FormId("charizard"),
            mega_form_id=FormId("charizard"),
            required_item_id=ItemId("charizardite-x"),
        )
