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


def test_ucs_with_unusual_costs_false_does_not_walk_through_a_trap():
    grid = make_grid("SXT")
    result = run_search(UCS([[0, None, 1]], unusual_costs=False), grid)

    assert result.path == []
    assert UCS([[0, None, 1]]).unusual_costs is False  # blocked is the default


def test_ucs_rejects_a_wrong_trap_cost_or_start_cost():
    grid = make_grid("SXT")
    # passable traps must cost exactly 6
    with pytest.raises(ValueError, match="must be 6"):
        run_search(UCS([[0, 5, 1]], unusual_costs=True), grid)
    # blocked traps must have no weight at all, even the old fixed cost
    with pytest.raises(ValueError, match="cannot have a weight"):
        run_search(UCS([[0, 6, 1]], unusual_costs=False), grid)
    # blocked mode: the start must cost 0
    with pytest.raises(ValueError):
        run_search(UCS([[1, None, 1]], unusual_costs=False), grid)


def test_ucs_unusual_costs_walks_through_a_trap_when_it_is_cheaper():
    # the detour along the bottom row costs 50 per cell, so the trap (6) is the cheaper way across
    grid = make_grid(
        "SXT",
        "...",
    )
    weights = [
        [1, 6, 1],
        [50, 50, 50],
    ]

    result = run_search(UCS(weights, unusual_costs=True), grid)

    assert result.path == [(0, 0), (0, 1), (0, 2)]
    # the start's own cost (1) counts: 1 + 6 + 1
    assert result.total_cost == 8


def test_ucs_unusual_costs_goes_around_a_trap_when_the_detour_is_cheaper():
    grid = make_grid(
        "SXT",
        "...",
    )
    weights = [
        [1, 6, 1],
        [1, 1, 1],
    ]

    result = run_search(UCS(weights, unusual_costs=True), grid)

    assert result.path == [(0, 0), (1, 0), (1, 1), (1, 2), (0, 2)]
    assert result.total_cost == 5
