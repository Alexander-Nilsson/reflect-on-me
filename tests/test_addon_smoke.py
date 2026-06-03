"""Smoke tests that verify the addon can be imported and hooks register."""

import pytest


class TestAddonImports:
    """Verify the addon module can be imported without errors."""

    def test_import_addon(self):
        """The addon should import cleanly."""
        import reflectOnMee

        assert reflectOnMee.ROMee_State is False
        assert reflectOnMee.AFFECTS_FILTERED_DECKS is False
        assert reflectOnMee.BT_JS is not None

    def test_hooks_registered(self):
        """Verify hooks are registered after import."""
        from unittest.mock import MagicMock

        import aqt
        from aqt import gui_hooks

        aqt.mw = MagicMock()

        import importlib

        import reflectOnMee

        importlib.reload(reflectOnMee)

        assert reflectOnMee.on_deck_conf_setup is not None
        assert reflectOnMee.on_load_config is not None
        assert reflectOnMee.on_save_config is not None
        assert reflectOnMee.on_show_answer is not None
        assert reflectOnMee.on_will_answer_card is not None


@pytest.mark.integration
class TestAddonIntegration:
    """Smoke tests that require a real Anki runtime."""

    def test_module_loads_in_anki_context(self, anki_session):
        """The addon should load when aqt.mw is set up."""
        from unittest.mock import MagicMock

        import aqt

        mw = MagicMock()
        mw.col = anki_session.collection
        aqt.mw = mw

        import importlib

        import reflectOnMee

        importlib.reload(reflectOnMee)

        assert reflectOnMee.ROMee_State is False
