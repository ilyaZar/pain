from __future__ import annotations

from Pain import (
    get_point_index_directional,
    get_point_index_growth,
)

# --- Growth model ---


class TestGetPointIndexGrowth:
    """Growth model separator selection."""

    def test_two_col_left_sign_positive(self) -> None:
        cell = [0, 0, 1, 1]
        cols = [0.0, 0.5, 1.0]
        idx, sign = get_point_index_growth(cell, cols, "width", 1)
        assert idx == 1
        assert sign == 1

    def test_two_col_right_sign_negative(self) -> None:
        cell = [1, 0, 2, 1]
        cols = [0.0, 0.5, 1.0]
        idx, sign = get_point_index_growth(cell, cols, "width", -1)
        assert idx == 1
        assert sign == -1

    def test_full_span_returns_minus_one(self) -> None:
        cell = [0, 0, 2, 1]
        cols = [0.0, 0.5, 1.0]
        idx, _sign = get_point_index_growth(cell, cols, "width", 1)
        assert idx == -1

    def test_three_col_middle(self) -> None:
        cell = [1, 0, 2, 1]
        cols = [0.0, 0.33, 0.67, 1.0]
        idx, sign = get_point_index_growth(cell, cols, "width", 1)
        assert idx == 2
        assert sign == 1

    def test_three_col_right_flips_sign(self) -> None:
        cell = [2, 0, 3, 1]
        cols = [0.0, 0.33, 0.67, 1.0]
        idx, sign = get_point_index_growth(cell, cols, "width", -1)
        # X_1=2 is chosen, but it's len-1=3? No, X_1=2.
        # sign<0 -> point_index = cell[X_1] = 2
        # 2 != 0 and 2 != 3 -> no edge case
        assert idx == 2
        assert sign == -1

    def test_two_row_top(self) -> None:
        cell = [0, 0, 1, 1]
        rows = [0.0, 0.5, 1.0]
        idx, sign = get_point_index_growth(cell, rows, "height", 1)
        assert idx == 1
        assert sign == 1

    def test_two_row_bottom(self) -> None:
        cell = [0, 1, 1, 2]
        rows = [0.0, 0.5, 1.0]
        idx, sign = get_point_index_growth(cell, rows, "height", -1)
        assert idx == 1
        assert sign == -1


# --- Directional model ---


class TestGetPointIndexDirectional:
    """Directional model separator selection."""

    def test_two_col_left(self) -> None:
        cell = [0, 0, 1, 1]
        cols = [0.0, 0.5, 1.0]
        idx, sign = get_point_index_directional(cell, cols, "width", 1)
        assert idx == 1
        assert sign == 1

    def test_two_col_right_falls_back(self) -> None:
        cell = [1, 0, 2, 1]
        cols = [0.0, 0.5, 1.0]
        idx, sign = get_point_index_directional(cell, cols, "width", 1)
        # X_2=2 is len-1 -> falls back to X_1=1
        assert idx == 1
        assert sign == 1  # sign preserved

    def test_full_span(self) -> None:
        cell = [0, 0, 2, 1]
        cols = [0.0, 0.5, 1.0]
        idx, _sign = get_point_index_directional(cell, cols, "width", 1)
        assert idx == -1

    def test_three_col_left(self) -> None:
        cell = [0, 0, 1, 1]
        cols = [0.0, 0.33, 0.67, 1.0]
        idx, sign = get_point_index_directional(cell, cols, "width", 1)
        assert idx == 1
        assert sign == 1

    def test_three_col_middle(self) -> None:
        cell = [1, 0, 2, 1]
        cols = [0.0, 0.33, 0.67, 1.0]
        idx, sign = get_point_index_directional(cell, cols, "width", 1)
        assert idx == 2
        assert sign == 1

    def test_three_col_right_falls_back(self) -> None:
        cell = [2, 0, 3, 1]
        cols = [0.0, 0.33, 0.67, 1.0]
        idx, sign = get_point_index_directional(cell, cols, "width", 1)
        # X_2=3 is len-1=3 -> falls back to X_1=2
        assert idx == 2
        assert sign == 1

    def test_two_row_bottom_falls_back(self) -> None:
        cell = [0, 1, 1, 2]
        rows = [0.0, 0.5, 1.0]
        idx, sign = get_point_index_directional(cell, rows, "height", 1)
        # Y_2=2 is len-1=2 -> falls back to Y_1=1
        assert idx == 1
        assert sign == 1
