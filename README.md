# ReflectOnMee

Anki addon that prevents **Reflex Grading Syndrome (RGS)** by enforcing a configurable pause before grading cards. When you reveal an answer too quickly (faster than your set limit), the grade buttons are hidden for a configurable pause period — forcing you to reflect before responding.

Forked from [Lovac42/ReflectOnMee](https://github.com/lovac42/ReflectOnMee), modernized for Anki 25.x.

## Installation

Download the `.ankiaddon` package from [Releases](https://github.com/Alexander-Nilsson/reflect-on-me/releases) and open it in Anki.

```bash
uv run python build.py all     # build from source
```

## Configuration

Configure per-deck in **Deck Options → Add-ons** tab:

| Setting | Description |
|---------|-------------|
| **Minimum think time** | Answer in less than this → you reflex graded → pause forces a slowdown (0 = off) |
| **Maximum think time** | Think longer than this → pause gives you a moment to absorb (0 = off) |
| **Pause duration** | How long grade buttons stay hidden |

A global option in the addon config (`config.json`) controls whether filtered decks are affected.

## Development

```bash
uv run pytest tests/                          # all tests
uv run pytest tests/ -m "not integration"     # unit tests only
uv run ruff check reflectOnMee.py tests/      # lint
uv run ruff format reflectOnMee.py tests/     # format
uv run pyright reflectOnMee.py                # type check
```

## License

GNU GPL v3 or later.
