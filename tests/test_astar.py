import random

import pytest

from algos.astar import ASTAR
from algos.ucs import UCS
from grid import EMPTY, START, STATIC_WALLS, TRAP, TRAP_COST, TREASURE
from helpers import assert_valid_path, make_grid, run_search


def test_astar_takes_a_longer_route_when_it_is_cheaper():
    grid = make_grid(
        "S.T",
        "...",
    )
    weights = [
        [0, 99, 1],
        [1, 1, 1],
    ]

    result = run_search(ASTAR(
        weights,
        unusual_costs=False
    ), grid)

    assert result.path == [(0, 0), (1, 0), (1, 1), (1, 2), (0, 2)]
    assert result.total_cost == 4
    assert_valid_path(grid, result.path)


def test_unusual_costs_controls_whether_astar_can_visit_traps_without_weights():
    grid = make_grid("SXT")

    passable = run_search(ASTAR(
        unusual_costs=True
    ), grid)
    blocked = run_search(ASTAR(
        unusual_costs=False
    ), grid)

    assert passable.path == [(0, 0), (0, 1), (0, 2)]
    assert passable.total_cost == 7
    assert blocked.path == []
    assert blocked.total_cost is None


def test_astar_returns_no_path_when_treasure_is_unreachable():
    grid = make_grid("S#T")

    result = run_search(ASTAR(
        unusual_costs=False
    ), grid)

    assert result.path == []
    assert result.total_cost is None
    assert result.nodes_expanded == 1


def test_astar_validates_treasures_and_weight_shape():
    with pytest.raises(ValueError, match="No treasure"):
        ASTAR().search(make_grid("S.."), 0, 0)
    with pytest.raises(ValueError, match="same size"):
        ASTAR([[0, 1]]).search(make_grid("S.T"), 0, 0)


def test_astar_goes_to_the_cheapest_of_several_treasures():
    # the first treasure in row-major order (0, 0) is 4 steps away, the other only 2
    grid = make_grid("T...S.T")

    result = run_search(ASTAR(unusual_costs=False), grid)

    assert result.path == [(0, 4), (0, 5), (0, 6)]
    assert result.total_cost == 2
    assert_valid_path(grid, result.path)


def test_astar_matches_ucs_cost_on_random_multi_treasure_maps():
    rng = random.Random(435)
    for _ in range(300):
        cells = [START] + [TREASURE] * 3 + [TRAP] * 2 + [STATIC_WALLS] * 15
        cells += [EMPTY] * (100 - len(cells))
        rng.shuffle(cells)
        grid = [cells[r * 10:(r + 1) * 10] for r in range(10)]
        weights = [
            [None if cell == STATIC_WALLS
             else TRAP_COST if cell == TRAP
             else 0 if cell == START
             else rng.randint(1, 9)
             for cell in row]
            for row in grid
        ]

        ucs = run_search(UCS(weights), grid)
        astar = run_search(ASTAR(weights), grid)

        assert astar.total_cost == ucs.total_cost
