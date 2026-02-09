"""Tests for command-level behaviour (Window-mocked).

Covers run() dispatch, equalize() with Window interaction,
PainToggleSettingCommand, and cycle/toggle helpers.
"""

from __future__ import annotations

from typing import Any
from unittest.mock import MagicMock, call, patch

import sublime

from Pain import (
    PainResizeCommand,
    PainToggleSettingCommand,
    WindowCommandSettings,
)

# -- Helpers --


class _DictSettings:
    """Dict-backed settings mock that supports get/set."""

    def __init__(self, data: dict[str, Any]) -> None:
        self._data = dict(data)

    def get(self, key: str, default: Any = None) -> Any:
        return self._data.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._data[key] = value


def _make_resize_cmd(
    layout: dict[str, Any] | None = None,
    active_group: int = 0,
    mode: str = "directional",
    amount: int = 3,
) -> PainResizeCommand:
    """Build a PainResizeCommand with a mocked window."""
    if layout is None:
        layout = {
            "cols": [0.0, 0.5, 1.0],
            "rows": [0.0, 1.0],
            "cells": [[0, 0, 1, 1], [1, 0, 2, 1]],
        }

    cmd = PainResizeCommand.__new__(PainResizeCommand)
    cmd.window = MagicMock()
    cmd.window.layout.return_value = layout
    cmd.window.active_group.return_value = active_group
    cmd.window.views_in_group.return_value = []
    cmd.window.active_view_in_group.return_value = MagicMock()

    settings = _DictSettings(
        {
            WindowCommandSettings.RESIZE_MODE: mode,
            WindowCommandSettings.RESIZE_AMOUNT: amount,
        }
    )
    cmd.settings = MagicMock(return_value=settings)  # type: ignore[method-assign]
    return cmd


def _make_toggle_cmd(
    data: dict[str, Any] | None = None,
) -> PainToggleSettingCommand:
    """Build a PainToggleSettingCommand with dict settings."""
    if data is None:
        data = {WindowCommandSettings.RESIZE_MODE: "directional"}

    cmd = PainToggleSettingCommand.__new__(PainToggleSettingCommand)
    cmd.window = MagicMock()

    settings = _DictSettings(data)
    cmd.settings = MagicMock(return_value=settings)  # type: ignore[method-assign]
    return cmd


# -- run() dispatch --


class TestRunDispatch:
    """run() dispatches to resize/equalize correctly."""

    def setup_method(self) -> None:
        PainResizeCommand._last_invalid_mode = None

    def test_decrease_calls_resize_negative(self) -> None:
        cmd = _make_resize_cmd(amount=5)
        with patch.object(cmd, "resize") as mock_resize:
            cmd.run("width", "decrease")
        mock_resize.assert_called_once_with("width", -5)

    def test_increase_calls_resize_positive(self) -> None:
        cmd = _make_resize_cmd(amount=5)
        with patch.object(cmd, "resize") as mock_resize:
            cmd.run("width", "increase")
        mock_resize.assert_called_once_with("width", 5)

    def test_equal_calls_equalize(self) -> None:
        cmd = _make_resize_cmd()
        with patch.object(cmd, "equalize") as mock_eq:
            cmd.run("all", "equal")
        mock_eq.assert_called_once_with("all")

    def test_unknown_resize_is_noop(self) -> None:
        cmd = _make_resize_cmd()
        with patch.object(cmd, "resize") as mock_r, patch.object(
            cmd, "equalize"
        ) as mock_e:
            cmd.run("width", "bogus")
        mock_r.assert_not_called()
        mock_e.assert_not_called()


# -- equalize() with Window --


class TestEqualizeCommand:
    """equalize() interacts with the Window correctly."""

    def test_width_sets_even_cols(self) -> None:
        layout = {
            "cols": [0.0, 0.8, 1.0],
            "rows": [0.0, 1.0],
            "cells": [[0, 0, 1, 1], [1, 0, 2, 1]],
        }
        cmd = _make_resize_cmd(layout=layout)
        cmd.equalize("width")

        applied = cmd.window.set_layout.call_args_list[-1][0][0]
        assert applied["cols"] == [0.0, 0.5, 1.0]
        assert applied["rows"] == [0.0, 1.0]

    def test_height_sets_even_rows(self) -> None:
        layout = {
            "cols": [0.0, 1.0],
            "rows": [0.0, 0.8, 1.0],
            "cells": [[0, 0, 1, 1], [0, 1, 1, 2]],
        }
        cmd = _make_resize_cmd(layout=layout)
        cmd.equalize("height")

        applied = cmd.window.set_layout.call_args_list[-1][0][0]
        assert applied["rows"] == [0.0, 0.5, 1.0]
        assert applied["cols"] == [0.0, 1.0]

    def test_all_equalizes_both(self) -> None:
        layout = {
            "cols": [0.0, 0.8, 1.0],
            "rows": [0.0, 0.2, 1.0],
            "cells": [
                [0, 0, 1, 1],
                [1, 0, 2, 1],
                [0, 1, 1, 2],
                [1, 1, 2, 2],
            ],
        }
        cmd = _make_resize_cmd(layout=layout)
        cmd.equalize("all")

        applied = cmd.window.set_layout.call_args_list[-1][0][0]
        assert applied["cols"] == [0.0, 0.5, 1.0]
        assert applied["rows"] == [0.0, 0.5, 1.0]

    def test_equalize_restores_focus(self) -> None:
        layout = {
            "cols": [0.0, 0.8, 1.0],
            "rows": [0.0, 1.0],
            "cells": [[0, 0, 1, 1], [1, 0, 2, 1]],
        }
        cmd = _make_resize_cmd(layout=layout, active_group=1)
        cmd.equalize("width")

        # focus_group should be called with the active group
        focus_calls = cmd.window.focus_group.call_args_list
        assert any(c == call(1) for c in focus_calls)


# -- PainToggleSettingCommand --


class TestToggleCommand:
    """Toggle command cycles modes and toggles booleans."""

    @patch.object(sublime, "save_settings")
    def test_cycle_resize_mode_directional_to_growth(
        self, _mock_save: MagicMock
    ) -> None:
        cmd = _make_toggle_cmd(
            {WindowCommandSettings.RESIZE_MODE: "directional"}
        )
        cmd.run(WindowCommandSettings.RESIZE_MODE)
        # After cycling, get_setting should return "growth"
        mode = cmd.settings().get(WindowCommandSettings.RESIZE_MODE)
        assert mode == "growth"

    @patch.object(sublime, "save_settings")
    def test_cycle_resize_mode_growth_to_directional(
        self, _mock_save: MagicMock
    ) -> None:
        cmd = _make_toggle_cmd({WindowCommandSettings.RESIZE_MODE: "growth"})
        cmd.run(WindowCommandSettings.RESIZE_MODE)
        mode = cmd.settings().get(WindowCommandSettings.RESIZE_MODE)
        assert mode == "directional"

    @patch.object(sublime, "save_settings")
    def test_toggle_boolean_false_to_true(self, _mock_save: MagicMock) -> None:
        cmd = _make_toggle_cmd(
            {
                WindowCommandSettings.RESIZE_MODE: "directional",
                WindowCommandSettings.GREEDY_PANE: False,
            }
        )
        cmd.run(WindowCommandSettings.GREEDY_PANE)
        val = cmd.settings().get(WindowCommandSettings.GREEDY_PANE)
        assert val is True

    @patch.object(sublime, "save_settings")
    def test_toggle_boolean_true_to_false(self, _mock_save: MagicMock) -> None:
        cmd = _make_toggle_cmd(
            {
                WindowCommandSettings.RESIZE_MODE: "directional",
                WindowCommandSettings.GREEDY_PANE: True,
            }
        )
        cmd.run(WindowCommandSettings.GREEDY_PANE)
        val = cmd.settings().get(WindowCommandSettings.GREEDY_PANE)
        assert val is False

    @patch.object(sublime, "save_settings")
    def test_save_settings_called(self, mock_save: MagicMock) -> None:
        cmd = _make_toggle_cmd()
        cmd.run(WindowCommandSettings.RESIZE_MODE)
        mock_save.assert_called_once_with(WindowCommandSettings.SETTINGS_FILE)
