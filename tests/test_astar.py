import pytest

from algos.astar import ASTAR
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
        unusual_costs=False,
        treasure_loc_row=0,
        treasure_loc_col=2,
    ), grid)

    assert result.path == [(0, 0), (1, 0), (1, 1), (1, 2), (0, 2)]
    assert result.total_cost == 4
    assert_valid_path(grid, result.path)


def test_unusual_costs_controls_whether_astar_can_visit_traps_without_weights():
    grid = make_grid("SXT")

    passable = run_search(ASTAR(
        unusual_costs=True,
        treasure_loc_row=0,
        treasure_loc_col=2,
    ), grid)
    blocked = run_search(ASTAR(
        unusual_costs=False,
        treasure_loc_row=0,
        treasure_loc_col=2,
    ), grid)

    assert passable.path == [(0, 0), (0, 1), (0, 2)]
    assert passable.total_cost == 7
    assert blocked.path == []
    assert blocked.total_cost is None


def test_astar_returns_no_path_when_treasure_is_unreachable():
    grid = make_grid("S#T")

    result = run_search(ASTAR(
        unusual_costs=False,
        treasure_loc_row=0,
        treasure_loc_col=2,
    ), grid)

    assert result.path == []
    assert result.total_cost is None
    assert result.nodes_expanded == 1


def test_astar_validates_treasure_location_and_weight_shape():
    grid = make_grid("S.T")

    with pytest.raises(ValueError, match="No treasure"):
        ASTAR(treasure_loc_row=0, treasure_loc_col=1).search(grid, 0, 0)
    with pytest.raises(ValueError, match="same size"):
        ASTAR([[0, 1]], treasure_loc_row=0, treasure_loc_col=2).search(grid, 0, 0)
