# AGENTS.md — ReflectOnMee

Anki addon that prevents Reflex Grading Syndrome (RGS) by enforcing a configurable pause before grading cards.

## Architecture

```
reflectOnMee.py    # Single-file addon: hooks, JS injection, deck config UI
__init__.py        # Entry point: imports reflectOnMee + version
config.json        # Anki addon config manager schema
```

## Runtime Behavior

- `gui_hooks.reviewer_did_show_answer` — after answer buttons appear, checks card time vs limit; if exceeded, runs JS to hide buttons for `rgs_pause` seconds
- `gui_hooks.reviewer_will_answer_card` — filter that returns `(False, ease)` when `ROMee_State` is True, blocking the grade
- `gui_hooks.deck_conf_did_setup_ui_form` — adds "RefxGrade Ans Limit" and "RefxGrade Pause" spinboxes in deck options → Reviews tab
- `gui_hooks.deck_conf_did_load_config` — loads `rgs_limit` / `rgs_pause` from config
- `gui_hooks.deck_conf_will_save_config` — saves `rgs_limit` / `rgs_pause` to config

## Deck Config Keys (stored in deck config dict)

- `rgs_limit` — seconds before the pause kicks in (0 = disabled)
- `rgs_pause` — seconds to wait before re-enabling grade buttons

## Critical Rules

- **No `engine/` layer** — this is a simple reviewer-hook addon, all in one file.
- **`card.time_taken()`** returns milliseconds, so `// 1000` gives seconds.
- **`card.current_deck_id()`** returns `odid` for filtered decks, `did` for regular decks.
- **Version in two places** — update both `pyproject.toml` AND `__init__.py`.
- **License is GPL-3.0-or-later**.

## Commands

```bash
uv run pytest tests/                         # all tests (needs anki/aqt installed)
uv run pytest tests/ -m "not integration"    # unit tests only
uv run ruff check reflectOnMee.py tests/     # lint
uv run pyright reflectOnMee.py               # type check
uv run python build.py all                   # clean -> build -> package .ankiaddon
```
