"""Smoke tests for the package."""

import pokemon_matchup


def test_package_is_importable() -> None:
    """Verify that the installed source package can be imported."""
    assert pokemon_matchup.__name__ == "pokemon_matchup"
