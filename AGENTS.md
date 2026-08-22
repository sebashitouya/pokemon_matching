# Repository instructions

## Development commands

- Install: `uv sync --frozen`
- Format: `uv run black .`
- Lint: `uv run ruff check .`
- Type check: `uv run mypy src`
- Test: `uv run pytest`

## Code conventions

- Use Python 3.12.
- Maximum line length is 88 characters.
- Add type annotations to every function.
- Use Google-style docstrings.
- Keep each function responsible for one operation.
- Randomized functions accept `seed: int = 42`.

## Architecture

- Keep data acquisition separate from domain logic.
- Keep matchup evaluation separate from team selection.
- Do not import infrastructure modules into domain modules.
- Represent each Pokémon form separately.

## Domain rules

- Unknown moves, items and abilities must remain unknown.
- Do not assume that an unobserved move is confirmed.
- Store source, retrieval date, season and regulation for external data.
- Distinguish between:
  - ability to switch in
  - ability to knock out
  - ability to temporarily stop
- Recommendations must include reasons and uncertainty.

## Code Review Rules

- Flag external data without provenance.
- Flag network access in unit tests.
- Require regression tests for scoring changes.
- Flag conclusions based only on type effectiveness.