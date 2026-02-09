"""Mock sublime and sublime_plugin for testing outside ST."""

from __future__ import annotations

import sys
import types
from unittest.mock import MagicMock


def _install_sublime_mocks() -> None:
    """Insert mock sublime modules into sys.modules."""
    sublime = types.ModuleType("sublime")
    sublime.Settings = MagicMock  # type: ignore[attr-defined]
    sublime.load_settings = MagicMock(  # type: ignore[attr-defined]
        return_value=MagicMock()
    )
    sublime.save_settings = MagicMock()  # type: ignore[attr-defined]
    sublime.error_message = MagicMock()  # type: ignore[attr-defined]

    sublime_plugin = types.ModuleType("sublime_plugin")
    sublime_plugin.WindowCommand = type(  # type: ignore[attr-defined]
        "WindowCommand", (), {"window": MagicMock()}
    )

    sys.modules["sublime"] = sublime
    sys.modules["sublime_plugin"] = sublime_plugin


_install_sublime_mocks()
