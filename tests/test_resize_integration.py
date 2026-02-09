"""Integration tests for the full resize logic.

These tests exercise the complete sign -> index -> boundary
-> value pipeline without mocking Sublime's Window.
"""

from __future__ import annotations

from Pain import (
    ACTIVE_GROUP,
    CELLS,
    COLS,
    ROWS,
    calc_point_value_in_boundaries,
    get_active_cell,
    get_indices,
    get_point_index_directional,
    get_point_index_growth,
    get_points,
    get_sign_directional,
    get_sign_growth,
    is_valid_point_value,
    set_points,
    sort_layout,
)


def _simulate_resize(
    layout: dict,
    dimension: str,
    amount: int,
    directional: bool,
) -> list[float]:
    """Run the resize pipeline on a layout dict.

    Returns the updated points list (cols or rows).
    """
    active_cell = get_active_cell(layout)
    points = list(get_points(layout, dimension))
    point, _ = get_indices(dimension)

    if directional:
        sign = get_sign_directional(active_cell[point], points)
        point_index, sign = get_point_index_directional(
            active_cell, points, dimension, sign
        )
    else:
        sign = get_sign_growth(active_cell[point], points)
        point_index, sign = get_point_index_growth(
            active_cell, points, dimension, sign
        )

    if point_index >= 0:
        amount *= sign
        if directional:
            point_min = points[point_index - 1]
            point_max = points[point_index + 1]
        else:
            point_min = 0.0
            point_max = 1.0

        new_value = calc_point_value_in_boundaries(
            points[point_index], amount, point_min, point_max
        )
        if is_valid_point_value(new_value, point_min, point_max):
            points[point_index] = new_value
            result = sort_layout(set_points(dict(layout), dimension, points))
            return get_points(result, dimension)

    return points


def _two_col(active: int = 0) -> dict:
    return {
        ACTIVE_GROUP: active,
        COLS: [0.0, 0.5, 1.0],
        ROWS: [0.0, 1.0],
        CELLS: [[0, 0, 1, 1], [1, 0, 2, 1]],
    }


def _three_col(active: int = 0) -> dict:
    return {
        ACTIVE_GROUP: active,
        COLS: [0.0, 0.33, 0.67, 1.0],
        ROWS: [0.0, 1.0],
        CELLS: [
            [0, 0, 1, 1],
            [1, 0, 2, 1],
            [2, 0, 3, 1],
        ],
    }


def _two_row(active: int = 0) -> dict:
    return {
        ACTIVE_GROUP: active,
        COLS: [0.0, 1.0],
        ROWS: [0.0, 0.5, 1.0],
        CELLS: [[0, 0, 1, 1], [0, 1, 1, 2]],
    }


# --- Growth model ---


class TestGrowthTwoCol:
    """Growth model: 2-column layout."""

    def test_left_increase_grows(self) -> None:
        pts = _simulate_resize(_two_col(0), "width", 1, directional=False)
        assert pts[1] > 0.5

    def test_left_decrease_shrinks(self) -> None:
        pts = _simulate_resize(_two_col(0), "width", -1, directional=False)
        assert pts[1] < 0.5

    def test_right_increase_grows(self) -> None:
        pts = _simulate_resize(_two_col(1), "width", 1, directional=False)
        # Growth model: increase from right -> separator
        # moves LEFT (grows right pane)
        assert pts[1] < 0.5

    def test_right_decrease_shrinks(self) -> None:
        pts = _simulate_resize(_two_col(1), "width", -1, directional=False)
        assert pts[1] > 0.5


# --- Directional model ---


class TestDirectionalTwoCol:
    """Directional model: 2-column layout."""

    def test_left_increase_pushes_right(self) -> None:
        pts = _simulate_resize(_two_col(0), "width", 1, directional=True)
        assert pts[1] > 0.5

    def test_left_decrease_pushes_left(self) -> None:
        pts = _simulate_resize(_two_col(0), "width", -1, directional=True)
        assert pts[1] < 0.5

    def test_right_increase_pushes_right(self) -> None:
        pts = _simulate_resize(_two_col(1), "width", 1, directional=True)
        # Directional: increase always rightward
        assert pts[1] > 0.5

    def test_right_decrease_pushes_left(self) -> None:
        pts = _simulate_resize(_two_col(1), "width", -1, directional=True)
        assert pts[1] < 0.5


class TestDirectionalThreeCol:
    """Directional model: 3-column layout."""

    def test_left_increase(self) -> None:
        pts = _simulate_resize(_three_col(0), "width", 1, directional=True)
        assert pts[1] > 0.33

    def test_middle_increase(self) -> None:
        pts = _simulate_resize(_three_col(1), "width", 1, directional=True)
        assert pts[2] > 0.67

    def test_right_increase(self) -> None:
        pts = _simulate_resize(_three_col(2), "width", 1, directional=True)
        # Right col: falls back to left boundary (idx 2),
        # pushes rightward -> separator moves right
        assert pts[2] > 0.67

    def test_right_decrease(self) -> None:
        pts = _simulate_resize(_three_col(2), "width", -1, directional=True)
        assert pts[2] < 0.67


class TestDirectionalTwoRow:
    """Directional model: 2-row layout."""

    def test_top_increase(self) -> None:
        pts = _simulate_resize(_two_row(0), "height", 1, directional=True)
        assert pts[1] > 0.5

    def test_bottom_increase(self) -> None:
        pts = _simulate_resize(_two_row(1), "height", 1, directional=True)
        assert pts[1] > 0.5

    def test_bottom_decrease(self) -> None:
        pts = _simulate_resize(_two_row(1), "height", -1, directional=True)
        assert pts[1] < 0.5
