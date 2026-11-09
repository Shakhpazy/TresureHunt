import random

import pytest

from algos.bfs import BFS
from algos.gbfs import GBFS
from grid import TRAP, TreasureMap
from helpers import assert_valid_path, make_grid, run_search


def test_gbfs_breaks_ties_by_smaller_row_plus_col_then_smaller_row():
    # from S, down (1,0) and right (0,1) both look 3 away from T. They tie on
    # row + col as well, so the smaller row wins and it goes right first.
    grid = make_grid(
        "S..",
        "...",
        "..T",
    )

    result = run_search(GBFS(), grid)

    assert result.path == [(0, 0), (0, 1), (0, 2), (1, 2), (2, 2)]
    assert_valid_path(grid, result.path)
    assert result.nodes_expanded == 5


def test_gbfs_priority_orders_by_h_then_row_plus_col_then_row():
    algo = GBFS()
    algo.treasures = [(5, 1), (0, 7)]

    # (1, 0) and (0, 2) are both 5 from their nearest treasure. (1, 0) has the
    # smaller row + col, so it goes first even though (0, 2) has the smaller row.
    assert algo._priority(1, 0) < algo._priority(0, 2)
    # equal h and equal row + col: the smaller row goes first
    assert algo._priority(0, 3) < algo._priority(1, 2)
    # a smaller h always beats everything else
    assert algo._priority(5, 2) < algo._priority(0, 0)


def test_gbfs_is_not_optimal_it_walks_into_the_pocket_above_the_treasure():
    grid = make_grid(
        "..#S..",
        "......",
        "......",
        "....##",
        ".....T",
    )

    greedy = run_search(GBFS(), grid)
    shortest = run_search(BFS(), grid)

    assert_valid_path(grid, greedy.path)
    assert len(shortest.path) == 7                      # 6 steps around the walls
    assert len(greedy.path) == 11                       # greedy needed 10


def test_gbfs_returns_no_path_when_the_treasure_is_unreachable():
    result = run_search(GBFS(), make_grid("S#T"))

    assert result.path == []
    assert result.nodes_expanded == 1


def test_gbfs_treats_a_trap_as_a_wall():
    assert run_search(GBFS(), make_grid("SXT")).path == []


def test_gbfs_validates_the_grid():
    with pytest.raises(ValueError, match="No treasure"):
        GBFS().search(make_grid("S.."), 0, 0)
    with pytest.raises(ValueError, match="No start"):
        GBFS().search(make_grid("S.T"), 0, 1)


def test_gbfs_goes_for_the_nearest_of_several_treasures():
    result = run_search(GBFS(), make_grid("T...S.T"))

    assert result.path == [(0, 4), (0, 5), (0, 6)]


def test_gbfs_finds_a_path_exactly_when_bfs_does_and_never_beats_it():
    random.seed(435)
    for _ in range(500):
        grid = TreasureMap(12, 25).getMap()

        greedy = run_search(GBFS(), grid)
        bfs = run_search(BFS(), grid)

        assert bool(greedy.path) == bool(bfs.path)
        if greedy.path:
            assert_valid_path(grid, greedy.path)
            assert len(greedy.path) >= len(bfs.path)
            assert not any(grid[r][c] == TRAP for r, c in greedy.visited)
