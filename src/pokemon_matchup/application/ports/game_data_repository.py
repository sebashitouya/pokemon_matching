"""Port for acquiring versioned game data."""

from typing import Protocol, runtime_checkable

from pokemon_matchup.domain.catalog import GameDataSnapshot


@runtime_checkable
class GameDataRepository(Protocol):
    """Acquire a complete game data snapshot."""

    def load(self) -> GameDataSnapshot:
        """Load and validate a game data snapshot.

        Returns:
            A complete, immutable game data snapshot.
        """
        ...
