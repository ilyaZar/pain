from __future__ import annotations

from Pain import (
    ACTIVE_GROUP,
    CELLS,
    COLS,
    ROWS,
    create_layout,
    sort_layout,
)


class TestCreateLayout:
    """Layout dictionary creation."""

    def test_basic_structure(self) -> None:
        layout = create_layout(0, [0.0, 1.0], [0.0, 1.0], [[0, 0, 1, 1]])
        assert layout[ACTIVE_GROUP] == 0
        assert layout[COLS] == [0.0, 1.0]
        assert layout[ROWS] == [0.0, 1.0]
        assert layout[CELLS] == [[0, 0, 1, 1]]

    def test_two_col(self) -> None:
        layout = create_layout(
            1,
            [0.0, 0.5, 1.0],
            [0.0, 1.0],
            [[0, 0, 1, 1], [1, 0, 2, 1]],
        )
        assert layout[ACTIVE_GROUP] == 1
        assert len(layout[CELLS]) == 2


class TestSortLayout:
    """Layout sorting preserves structure."""

    def test_already_sorted(self) -> None:
        layout = {
            ACTIVE_GROUP: 0,
            COLS: [0.0, 0.5, 1.0],
            ROWS: [0.0, 1.0],
            CELLS: [[0, 0, 1, 1], [1, 0, 2, 1]],
        }
        result = sort_layout(layout)
        assert result[COLS] == [0.0, 0.5, 1.0]
        assert result[ROWS] == [0.0, 1.0]
        assert result[CELLS] == [
            [0, 0, 1, 1],
            [1, 0, 2, 1],
        ]

    def test_preserves_active_group(self) -> None:
        layout = {
            ACTIVE_GROUP: 1,
            COLS: [0.0, 0.5, 1.0],
            ROWS: [0.0, 1.0],
            CELLS: [[0, 0, 1, 1], [1, 0, 2, 1]],
        }
        result = sort_layout(layout)
        assert result[ACTIVE_GROUP] == 1

    def test_three_col_sorted(self) -> None:
        layout = {
            ACTIVE_GROUP: 0,
            COLS: [0.0, 0.33, 0.67, 1.0],
            ROWS: [0.0, 1.0],
            CELLS: [
                [0, 0, 1, 1],
                [1, 0, 2, 1],
                [2, 0, 3, 1],
            ],
        }
        result = sort_layout(layout)
        assert result[COLS] == [0.0, 0.33, 0.67, 1.0]
        assert len(result[CELLS]) == 3

    def test_grid_layout(self) -> None:
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
        result = sort_layout(layout)
        assert len(result[CELLS]) == 4
        assert result[COLS] == [0.0, 0.5, 1.0]
        assert result[ROWS] == [0.0, 0.5, 1.0]
