"""Battle format and regulation models."""

from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum

from pokemon_matchup.domain.identifiers import BuildId, RegulationId


class BattleFormat(StrEnum):
    """A supported battlefield format."""

    SINGLE = "single"
    DOUBLE = "double"


@dataclass(frozen=True, slots=True)
class Regulation:
    """Team and selection constraints for a battle regulation."""

    id: RegulationId
    name: str
    battle_format: BattleFormat
    team_size: int
    selection_size: int
    lead_size: int
    max_mega_evolutions: int

    def __post_init__(self) -> None:
        """Validate regulation identifiers and numeric constraints."""
        if not self.id.strip():
            raise ValueError("regulation id must not be blank")
        if not self.name.strip():
            raise ValueError("regulation name must not be blank")
        if self.team_size < 1:
            raise ValueError("team size must be positive")
        if not 1 <= self.selection_size <= self.team_size:
            raise ValueError("selection size must be between one and team size")
        if not 1 <= self.lead_size <= self.selection_size:
            raise ValueError("lead size must be between one and selection size")
        expected_lead_size = 1 if self.battle_format is BattleFormat.SINGLE else 2
        if self.lead_size != expected_lead_size:
            raise ValueError(
                f"{self.battle_format.value} battles require a lead size of "
                f"{expected_lead_size}"
            )
        if not 0 <= self.max_mega_evolutions <= self.selection_size:
            raise ValueError(
                "maximum Mega Evolutions must be between zero and selection size"
            )

    def validate_team(self, build_ids: Sequence[BuildId]) -> None:
        """Validate a complete team against this regulation.

        Args:
            build_ids: Registered build identifiers in the team.
        """
        self._validate_build_ids(build_ids, self.team_size, "team")

    def validate_selection(self, build_ids: Sequence[BuildId]) -> None:
        """Validate a battle selection against this regulation.

        Args:
            build_ids: Registered build identifiers selected for battle.
        """
        self._validate_build_ids(build_ids, self.selection_size, "selection")

    @staticmethod
    def _validate_build_ids(
        build_ids: Sequence[BuildId], expected_size: int, label: str
    ) -> None:
        """Validate collection size, identifier content, and uniqueness.

        Args:
            build_ids: Build identifiers to validate.
            expected_size: Required number of identifiers.
            label: Human-readable collection label.
        """
        if len(build_ids) != expected_size:
            raise ValueError(f"{label} must contain exactly {expected_size} builds")
        if any(not build_id.strip() for build_id in build_ids):
            raise ValueError(f"{label} build ids must not be blank")
        if len(set(build_ids)) != len(build_ids):
            raise ValueError(f"{label} must not contain duplicate builds")
