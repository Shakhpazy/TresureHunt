from algos.bfs import BFS
from helpers import assert_valid_path, make_grid, run_search


def test_bfs_finds_a_shortest_path_across_an_open_grid():
    # the treasure is 2 rows and 3 columns away, so any shortest path takes 5 steps
    grid = make_grid(
        "S...",
        "....",
        "...T",
    )

    result = run_search(BFS(), grid)

    assert len(result.path) - 1 == 5
    assert_valid_path(grid, result.path)
    # the treasure is the only cell 5 steps away, so BFS expands every cell: 12 in total
    assert result.nodes_expanded == 12


def test_bfs_goes_around_a_trap_that_blocks_the_direct_route():
    # straight along the top row is blocked by the trap; the only 4-step route is
    # down, right, right, up
    grid = make_grid(
        "SXT",
        "...",
        "..#",
    )

    result = run_search(BFS(), grid)

    assert result.path == [(0, 0), (1, 0), (1, 1), (1, 2), (0, 2)]
    assert result.nodes_expanded == 7
    assert (0, 1) not in result.visited


def test_bfs_finds_nothing_when_a_wall_splits_the_grid():
    grid = make_grid(
        "S#T",
        ".#.",
        ".#.",
    )

    result = run_search(BFS(), grid)

    assert result.path == []
    assert result.visited == {(0, 0), (1, 0), (2, 0)}
    assert result.nodes_expanded == 3
