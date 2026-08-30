"""Tests for game data snapshot provenance and integrity."""

from datetime import date

import pytest

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


def _provenance() -> DataProvenance:
    """Create valid provenance for catalog tests.

    Returns:
        Valid test provenance.
    """
    return DataProvenance(
        source="official-source",
        retrieved_on=date(2026, 8, 30),
        season="2026-08",
        regulation_id=RegulationId("champions-single"),
    )


def _form(form_id: str, species_id: str) -> PokemonForm:
    """Create a valid form for catalog tests.

    Args:
        form_id: Form identifier value.
        species_id: Owning species identifier value.

    Returns:
        Valid test form.
    """
    return PokemonForm(
        id=FormId(form_id),
        species_id=SpeciesId(species_id),
        name=form_id,
        types=(PokemonType.FIRE,),
        base_stats=BaseStats(1, 1, 1, 1, 1, 1),
    )


def test_snapshot_rejects_duplicate_species_ids() -> None:
    """Reject two species records with the same identifier."""
    species = PokemonSpecies(SpeciesId("charizard"), "Charizard")

    with pytest.raises(ValueError, match="species ids must be unique"):
        GameDataSnapshot(_provenance(), (species, species), (), ())


def test_snapshot_rejects_form_with_unknown_species() -> None:
    """Reject a form whose owning species is absent."""
    with pytest.raises(ValueError, match="references unknown species"):
        GameDataSnapshot(_provenance(), (), (_form("charizard", "charizard"),), ())


def test_snapshot_rejects_mega_evolution_across_species() -> None:
    """Reject a Mega Evolution connecting forms from different species."""
    species = (
        PokemonSpecies(SpeciesId("charizard"), "Charizard"),
        PokemonSpecies(SpeciesId("venusaur"), "Venusaur"),
    )
    forms = (
        _form("charizard", "charizard"),
        _form("mega-venusaur", "venusaur"),
    )
    mega_evolution = MegaEvolution(
        MegaEvolutionId("invalid"),
        FormId("charizard"),
        FormId("mega-venusaur"),
        ItemId("invalid-stone"),
    )

    with pytest.raises(ValueError, match="must link forms of one species"):
        GameDataSnapshot(_provenance(), species, forms, (mega_evolution,))
