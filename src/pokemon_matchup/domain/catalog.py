"""Versioned game data catalog models and integrity rules."""

from dataclasses import dataclass
from datetime import date

from pokemon_matchup.domain.identifiers import RegulationId
from pokemon_matchup.domain.pokemon import MegaEvolution, PokemonForm, PokemonSpecies


@dataclass(frozen=True, slots=True)
class DataProvenance:
    """Provenance required for an external game data snapshot."""

    source: str
    retrieved_on: date
    season: str
    regulation_id: RegulationId

    def __post_init__(self) -> None:
        """Validate required provenance text and identifier fields."""
        if not self.source.strip():
            raise ValueError("data source must not be blank")
        if not self.season.strip():
            raise ValueError("data season must not be blank")
        if not self.regulation_id.strip():
            raise ValueError("data regulation id must not be blank")


@dataclass(frozen=True, slots=True)
class GameDataSnapshot:
    """An immutable and internally consistent game data snapshot."""

    provenance: DataProvenance
    species: tuple[PokemonSpecies, ...]
    forms: tuple[PokemonForm, ...]
    mega_evolutions: tuple[MegaEvolution, ...]

    def __post_init__(self) -> None:
        """Validate unique identifiers and cross-record references."""
        species_by_id = {record.id: record for record in self.species}
        forms_by_id = {record.id: record for record in self.forms}
        mega_by_id = {record.id: record for record in self.mega_evolutions}

        if len(species_by_id) != len(self.species):
            raise ValueError("species ids must be unique")
        if len(forms_by_id) != len(self.forms):
            raise ValueError("form ids must be unique")
        if len(mega_by_id) != len(self.mega_evolutions):
            raise ValueError("Mega Evolution ids must be unique")

        for form in self.forms:
            if form.species_id not in species_by_id:
                raise ValueError(
                    f"form {form.id} references unknown species {form.species_id}"
                )

        for mega_evolution in self.mega_evolutions:
            base_form = forms_by_id.get(mega_evolution.base_form_id)
            mega_form = forms_by_id.get(mega_evolution.mega_form_id)
            if base_form is None:
                raise ValueError(
                    "Mega Evolution "
                    f"{mega_evolution.id} references unknown base form "
                    f"{mega_evolution.base_form_id}"
                )
            if mega_form is None:
                raise ValueError(
                    "Mega Evolution "
                    f"{mega_evolution.id} references unknown Mega-Evolved form "
                    f"{mega_evolution.mega_form_id}"
                )
            if base_form.species_id != mega_form.species_id:
                raise ValueError(
                    f"Mega Evolution {mega_evolution.id} must link forms of one species"
                )
