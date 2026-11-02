import pytest

from algos.ucs import UCS
from helpers import assert_valid_path, make_grid, run_search


def test_ucs_takes_a_longer_route_when_it_is_cheaper():
    # straight across the top is 2 steps but costs 99 + 1 = 100;
    # around the bottom is 4 steps and costs 1 + 1 + 1 + 1 = 4
    grid = make_grid(
        "S.T",
        "...",
    )
    weights = [
        [0, 99, 1],
        [1, 1, 1],
    ]

    result = run_search(UCS(weights), grid)

    assert result.path == [(0, 0), (1, 0), (1, 1), (1, 2), (0, 2)]
    assert result.total_cost == 4
    # popped in cost order: costs 0, 1, 2, 3, then the treasure at 4, before (0, 1) at 99
    assert result.nodes_expanded == 5


def test_ucs_cost_equals_the_number_of_steps_when_every_weight_is_one():
    grid = make_grid(
        "S..",
        "...",
        "..T",
    )
    weights = [
        [0, 1, 1],
        [1, 1, 1],
        [1, 1, 1],
    ]

    result = run_search(UCS(weights), grid)

    assert len(result.path) - 1 == 4
    assert result.total_cost == 4
    assert_valid_path(grid, result.path)
    # the treasure is the only cell with cost 4, so every other cell is expanded first
    assert result.nodes_expanded == 9


def test_ucs_rejects_weights_that_do_not_match_the_grid():
    # the wall at (0, 1) was given a weight, as if the weights belonged to another map
    grid = make_grid(
        "S#T",
        "...",
    )
    weights = [
        [0, 5, 1],
        [1, 1, 1],
    ]

    with pytest.raises(ValueError, match="do not match the grid"):
        UCS(weights).search(grid, 0, 0)
