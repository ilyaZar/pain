"""Tests for the equalize logic.

Exercises the pure function pipeline that equalize() uses:
get_points -> compute even spacing -> set_points.
"""

from __future__ import annotations

import pytest

from Pain import (
    ACTIVE_GROUP,
    CELLS,
    COLS,
    ROWS,
    get_points,
    set_points,
)


def _equalize(layout: dict, dimension: str) -> dict:
    """Equalize a single dimension (pure function version)."""
    points = get_points(layout, dimension)
    length = len(points)
    points = [i * (1 / (length - 1)) for i in range(length)]
    return set_points(layout, dimension, points)


def _equalize_all(layout: dict) -> dict:
    """Equalize both dimensions (pure function version)."""
    layout = _equalize(layout, "width")
    layout = _equalize(layout, "height")
    return layout


# --- Fixtures ---


def _two_col_uneven() -> dict:
    return {
        ACTIVE_GROUP: 0,
        COLS: [0.0, 0.8, 1.0],
        ROWS: [0.0, 1.0],
        CELLS: [[0, 0, 1, 1], [1, 0, 2, 1]],
    }


def _three_col_uneven() -> dict:
    return {
        ACTIVE_GROUP: 0,
        COLS: [0.0, 0.1, 0.9, 1.0],
        ROWS: [0.0, 1.0],
        CELLS: [
            [0, 0, 1, 1],
            [1, 0, 2, 1],
            [2, 0, 3, 1],
        ],
    }


def _two_row_uneven() -> dict:
    return {
        ACTIVE_GROUP: 0,
        COLS: [0.0, 1.0],
        ROWS: [0.0, 0.8, 1.0],
        CELLS: [[0, 0, 1, 1], [0, 1, 1, 2]],
    }


def _grid_2x2_uneven() -> dict:
    return {
        ACTIVE_GROUP: 0,
        COLS: [0.0, 0.7, 1.0],
        ROWS: [0.0, 0.3, 1.0],
        CELLS: [
            [0, 0, 1, 1],
            [1, 0, 2, 1],
            [0, 1, 1, 2],
            [1, 1, 2, 2],
        ],
    }


def _single_pane() -> dict:
    return {
        ACTIVE_GROUP: 0,
        COLS: [0.0, 1.0],
        ROWS: [0.0, 1.0],
        CELLS: [[0, 0, 1, 1]],
    }


def _seven_pane() -> dict:
    """The 7-pane layout from the README."""
    return {
        ACTIVE_GROUP: 0,
        COLS: [0.0, 0.4, 0.55, 0.85, 1.0],
        ROWS: [0.0, 0.45, 0.7, 1.0],
        CELLS: [
            [0, 0, 1, 3],  # pane 1
            [1, 0, 3, 1],  # pane 2
            [3, 0, 4, 1],  # pane 3
            [1, 1, 2, 2],  # pane 4
            [2, 1, 3, 3],  # pane 5
            [3, 1, 4, 3],  # pane 6
            [1, 2, 2, 3],  # pane 7
        ],
    }


# --- Equalize width ---


class TestEqualizeWidth:
    """Equalize column separators."""

    def test_two_col_uneven(self) -> None:
        layout = _equalize(_two_col_uneven(), "width")
        assert layout[COLS] == [0.0, 0.5, 1.0]

    def test_three_col_uneven(self) -> None:
        layout = _equalize(_three_col_uneven(), "width")
        cols = layout[COLS]
        assert len(cols) == 4
        assert cols[0] == 0.0
        assert cols[-1] == 1.0
        assert cols[1] == pytest.approx(1 / 3)
        assert cols[2] == pytest.approx(2 / 3)

    def test_rows_untouched(self) -> None:
        layout = _equalize(_grid_2x2_uneven(), "width")
        assert layout[ROWS] == [0.0, 0.3, 1.0]

    def test_cells_untouched(self) -> None:
        orig_cells = [list(c) for c in _two_col_uneven()[CELLS]]
        layout = _equalize(_two_col_uneven(), "width")
        assert layout[CELLS] == orig_cells


# --- Equalize height ---


class TestEqualizeHeight:
    """Equalize row separators."""

    def test_two_row_uneven(self) -> None:
        layout = _equalize(_two_row_uneven(), "height")
        assert layout[ROWS] == [0.0, 0.5, 1.0]

    def test_cols_untouched(self) -> None:
        layout = _equalize(_grid_2x2_uneven(), "height")
        assert layout[COLS] == [0.0, 0.7, 1.0]


# --- Equalize all ---


class TestEqualizeAll:
    """Equalize both dimensions at once."""

    def test_grid_both_equalized(self) -> None:
        layout = _equalize_all(_grid_2x2_uneven())
        assert layout[COLS] == [0.0, 0.5, 1.0]
        assert layout[ROWS] == [0.0, 0.5, 1.0]

    def test_seven_pane_cols(self) -> None:
        layout = _equalize_all(_seven_pane())
        cols = layout[COLS]
        assert len(cols) == 5
        assert cols[0] == 0.0
        assert cols[-1] == 1.0
        assert cols[1] == pytest.approx(0.25)
        assert cols[2] == pytest.approx(0.5)
        assert cols[3] == pytest.approx(0.75)

    def test_seven_pane_rows(self) -> None:
        layout = _equalize_all(_seven_pane())
        rows = layout[ROWS]
        assert len(rows) == 4
        assert rows[0] == 0.0
        assert rows[-1] == 1.0
        assert rows[1] == pytest.approx(1 / 3)
        assert rows[2] == pytest.approx(2 / 3)

    def test_seven_pane_cells_preserved(self) -> None:
        orig = _seven_pane()
        orig_cells = [list(c) for c in orig[CELLS]]
        layout = _equalize_all(orig)
        assert layout[CELLS] == orig_cells


# --- Edge cases ---


class TestEqualizeEdgeCases:
    """Edge cases and idempotency."""

    def test_single_pane_width_noop(self) -> None:
        layout = _equalize(_single_pane(), "width")
        assert layout[COLS] == [0.0, 1.0]

    def test_single_pane_height_noop(self) -> None:
        layout = _equalize(_single_pane(), "height")
        assert layout[ROWS] == [0.0, 1.0]

    def test_already_equal_is_idempotent(self) -> None:
        layout = {
            ACTIVE_GROUP: 0,
            COLS: [0.0, 0.5, 1.0],
            ROWS: [0.0, 0.5, 1.0],
            CELLS: [
                [0, 0, 1, 1],
                [1, 0, 2, 1],
                [0, 1, 1, 2],
                [1, 1, 2, 2],
            ],
        }
        result = _equalize_all(layout)
        assert result[COLS] == [0.0, 0.5, 1.0]
        assert result[ROWS] == [0.0, 0.5, 1.0]
