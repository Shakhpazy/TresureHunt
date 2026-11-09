import random

from grid import MAX_WEIGHT, MIN_WEIGHT, create_weight_matrix
from helpers import make_grid


def test_random_weights_only_touch_empty_cells():
    random.seed(1)
    grid = make_grid(
        "S.#.",
        ".XT.",
    )

    for _ in range(200):
        weights = create_weight_matrix(grid, random_weights=True)

        assert weights[0][0] == 0                                  # start
        assert weights[0][2] is None and weights[1][1] is None     # wall, blocked trap
        assert weights[1][2] == 1                                  # treasure
        for r, c in ((0, 1), (0, 3), (1, 0), (1, 3)):              # empty cells
            assert MIN_WEIGHT <= weights[r][c] <= MAX_WEIGHT


def test_random_weights_actually_vary_and_reach_both_ends_of_the_range():
    random.seed(2)
    grid = [["."] * 30 for _ in range(30)]
    grid[0][0] = "S"
    grid[1][1] = "T"
    grid = make_grid(*("".join(row) for row in grid))

    weights = create_weight_matrix(grid, random_weights=True)
    values = {w for row in weights for w in row if w not in (0, None)}

    assert len(values) > 50
    assert min(values) == MIN_WEIGHT and max(values) == MAX_WEIGHT


def test_weights_stay_constant_unless_random_weights_is_asked_for():
    grid = make_grid("S.XT")

    assert create_weight_matrix(grid, traps_passable=True) == [[0, 1, 6, 1]]
    assert create_weight_matrix(grid) == [[0, 1, None, 1]]
