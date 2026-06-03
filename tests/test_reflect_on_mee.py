"""Unit tests for ReflectOnMee addon logic."""

import importlib
import json
from unittest.mock import MagicMock, patch

import pytest


def _reload_addon():
    """Reload reflectOnMee so it picks up the current aqt.mw."""
    import reflectOnMee

    importlib.reload(reflectOnMee)
    return reflectOnMee


class TestKeysOff:
    """Test the keys_off function that toggles ROMee_State."""

    def test_keys_off_true(self):
        mod = _reload_addon()
        mod.keys_off(True)
        assert mod.ROMee_State is True

    def test_keys_off_false(self):
        mod = _reload_addon()
        mod.keys_off(False)
        assert mod.ROMee_State is False


class TestEval:
    """Test the eval function that disables buttons on a timer."""

    def test_eval_disables_buttons(self):
        import aqt

        aqt.mw = MagicMock()
        aqt.mw.reviewer = MagicMock()
        aqt.mw.reviewer.bottom.web.eval = MagicMock()

        mod = _reload_addon()

        with (
            patch.object(mod, "keys_off") as mock_keys_off,
            patch("reflectOnMee.QTimer") as mock_timer,
        ):
            mod.eval(5)

            mock_keys_off.assert_any_call(True)

            js = mod.BT_JS % 5
            aqt.mw.reviewer.bottom.web.eval.assert_called_once_with(js)

            args, _ = mock_timer.singleShot.call_args
            assert args[0] == 5000
            assert callable(args[1])


class TestOnShowAnswer:
    """Test the on_show_answer hook handler."""

    def _setup_mw(self, config: dict | None = None):
        import aqt

        aqt.mw = MagicMock()
        aqt.mw.col.decks.config_dict_for_deck_id = MagicMock()
        aqt.mw.col.decks.config_dict_for_deck_id.return_value = config or {}
        return _reload_addon()

    def test_skips_filtered_decks_when_disabled(self):
        mod = self._setup_mw()

        card = MagicMock()
        card.odid = 5
        mod.AFFECTS_FILTERED_DECKS = False

        with patch.object(mod, "eval") as mock_eval:
            mod.on_show_answer(card)
            mock_eval.assert_not_called()

    def test_skips_when_limit_is_zero(self):
        mod = self._setup_mw({"rgs_limit": 0})

        card = MagicMock()
        card.odid = 0
        card.current_deck_id.return_value = 1
        mod.AFFECTS_FILTERED_DECKS = False

        with patch.object(mod, "eval") as mock_eval:
            mod.on_show_answer(card)
            mock_eval.assert_not_called()

    def test_triggers_eval_when_over_limit(self):
        mod = self._setup_mw({"rgs_limit": 5, "rgs_pause": 3})

        card = MagicMock()
        card.odid = 0
        card.current_deck_id.return_value = 1
        card.time_taken.return_value = 10000
        mod.AFFECTS_FILTERED_DECKS = False

        with patch.object(mod, "eval") as mock_eval:
            mod.on_show_answer(card)
            mock_eval.assert_called_once_with(3)

    def test_triggers_short_eval_for_learning_cards(self):
        mod = self._setup_mw({"rgs_limit": 10, "rgs_pause": 5})

        card = MagicMock()
        card.odid = 0
        card.current_deck_id.return_value = 1
        card.time_taken.return_value = 3000
        card.queue = 1
        mod.AFFECTS_FILTERED_DECKS = False

        with patch.object(mod, "eval") as mock_eval:
            mod.on_show_answer(card)
            mock_eval.assert_called_once_with(3)


class TestDeckOptionsLoaded:
    """Test the on_deck_options_loaded hook handler."""

    def test_injects_html_and_js(self):
        import aqt

        aqt.mw = MagicMock()

        mod = _reload_addon()
        dialog = MagicMock()
        dialog.web.eval = MagicMock()
        expected_html = mod.DECKOPTIONS_HTML

        mod.on_deck_options_loaded(dialog)

        dialog.web.eval.assert_called_once()
        call_arg = dialog.web.eval.call_args[0][0]
        assert json.dumps(expected_html) in call_arg
        assert "$deckOptions.then" in call_arg


class TestOnWillAnswerCard:
    """Test the reviewer_will_answer_card filter."""

    def test_allows_answer_when_no_state(self):
        mod = _reload_addon()
        mod.ROMee_State = False
        result = mod.on_will_answer_card((True, 3), MagicMock(), MagicMock())
        assert result == (True, 3)

    def test_blocks_answer_when_romee_state(self):
        mod = _reload_addon()
        mod.ROMee_State = True
        result = mod.on_will_answer_card((True, 2), MagicMock(), MagicMock())
        assert result == (False, 2)

    def test_preserves_ease_value(self):
        mod = _reload_addon()
        for ease in (1, 2, 3, 4):
            mod.ROMee_State = True
            result = mod.on_will_answer_card((True, ease), MagicMock(), MagicMock())
            assert result == (False, ease)
