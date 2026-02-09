from __future__ import annotations

from Pain import get_sign_directional, get_sign_growth


class TestGetSignGrowth:
    """Growth model sign determination."""

    def test_two_col_left(self) -> None:
        cols = [0.0, 0.5, 1.0]
        assert get_sign_growth(0, cols) == 1

    def test_two_col_right(self) -> None:
        cols = [0.0, 0.5, 1.0]
        assert get_sign_growth(1, cols) == -1

    def test_three_col_left(self) -> None:
        cols = [0.0, 0.33, 0.67, 1.0]
        assert get_sign_growth(0, cols) == 1

    def test_three_col_middle(self) -> None:
        cols = [0.0, 0.33, 0.67, 1.0]
        assert get_sign_growth(1, cols) == 1

    def test_three_col_right(self) -> None:
        cols = [0.0, 0.33, 0.67, 1.0]
        assert get_sign_growth(2, cols) == -1

    def test_four_col_first(self) -> None:
        cols = [0.0, 0.25, 0.5, 0.75, 1.0]
        assert get_sign_growth(0, cols) == 1

    def test_four_col_second(self) -> None:
        cols = [0.0, 0.25, 0.5, 0.75, 1.0]
        assert get_sign_growth(1, cols) == 1

    def test_four_col_third(self) -> None:
        cols = [0.0, 0.25, 0.5, 0.75, 1.0]
        assert get_sign_growth(2, cols) == -1

    def test_four_col_fourth(self) -> None:
        cols = [0.0, 0.25, 0.5, 0.75, 1.0]
        assert get_sign_growth(3, cols) == -1

    def test_two_row_top(self) -> None:
        rows = [0.0, 0.5, 1.0]
        assert get_sign_growth(0, rows) == 1

    def test_two_row_bottom(self) -> None:
        rows = [0.0, 0.5, 1.0]
        assert get_sign_growth(1, rows) == -1


class TestGetSignDirectional:
    """Directional model always returns +1."""

    def test_always_positive_left(self) -> None:
        assert get_sign_directional(0, [0.0, 0.5, 1.0]) == 1

    def test_always_positive_right(self) -> None:
        assert get_sign_directional(1, [0.0, 0.5, 1.0]) == 1

    def test_always_positive_three_col(self) -> None:
        cols = [0.0, 0.33, 0.67, 1.0]
        for i in range(3):
            assert get_sign_directional(i, cols) == 1
