import pytest

from custom_grid import build_custom_grid, build_custom_weights


def test_every_item_lands_on_exactly_the_requested_cell():
    grid = build_custom_grid((0, 0), [(1, 1), (2, 0)], (2, 2), [(0, 1), (3, 3)], size=4)

    assert grid[0][0] == "S"
    assert grid[1][1] == "X" and grid[2][0] == "X"
    assert sum(cell == "X" for row in grid for cell in row) == 2
    assert grid[2][2] == "T"
    assert grid[0][1] == "#" and grid[3][3] == "#"
    assert sum(cell == "#" for row in grid for cell in row) == 2


@pytest.mark.parametrize("start, trap, treasure, walls", [
    ((0, 0), [(1, 1)], (4, 0), []),            # outside the grid
    ((0, 0), [(1, 1)], (2, 2), [(-1, 0)]),     # negative wall position
    ((0, 0), [(0, 0)], (2, 2), []),            # trap on the start
    ((0, 0), [(1, 1)], (2, 2), [(1, 1)]),      # wall on the trap
    ((0, 0), [(1, 1)], (2, 2), [(3, 3), (3, 3)]),  # two walls on one cell
    ((0, 0), [(1, 1), (1, 1)], (2, 2), []),    # two traps on one cell
    ((0, 0), [(1, 1), (5, 5)], (2, 2), []),    # second trap outside the grid
])
def test_invalid_layouts_are_rejected(start, trap, treasure, walls):
    with pytest.raises(ValueError):
        build_custom_grid(start, trap, treasure, walls, size=4)


def test_weights_give_the_start_and_every_trap_their_special_costs_and_walls_none():
    grid = build_custom_grid((0, 0), [(1, 1), (2, 0)], (2, 2), [(3, 3)], size=4)

    weights = build_custom_weights(grid, (0, 0))

    assert weights[0][0] == 1
    assert weights[1][1] == 6 and weights[2][0] == 6
    assert weights[3][3] is None
