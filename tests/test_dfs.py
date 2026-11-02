from algos.dfs import DFS
from helpers import assert_valid_path, make_grid, run_search


def test_dfs_snakes_around_instead_of_taking_the_shortest_path():
    # DFS pops the neighbour it pushed last, so it prefers LEFT, UP, RIGHT, DOWN
    # (DIRECTIONS is DOWN, RIGHT, UP, LEFT). From the top-left corner it sweeps
    # right along the top row, drops down and comes back along the middle row,
    # even though the treasure is only two steps straight down.
    grid = make_grid(
        "S..",
        "...",
        "T..",
    )

    result = run_search(DFS(), grid)

    assert result.path == [(0, 0), (0, 1), (0, 2), (1, 2), (1, 1), (1, 0), (2, 0)]
    assert len(result.path) - 1 == 6
    assert result.nodes_expanded == 7
    assert_valid_path(grid, result.path)


def test_dfs_follows_the_only_route_around_walls_and_a_trap():
    # the wall and the trap leave a single corridor: down, along the bottom, back up
    grid = make_grid(
        "S#T",
        ".X.",
        "...",
    )

    result = run_search(DFS(), grid)

    assert result.path == [(0, 0), (1, 0), (2, 0), (2, 1), (2, 2), (1, 2), (0, 2)]
    assert result.nodes_expanded == 7
    assert (0, 1) not in result.visited
    assert (1, 1) not in result.visited


def test_dfs_finds_nothing_when_the_treasure_is_walled_off():
    grid = make_grid(
        "S.#",
        "..#",
        "##T",
    )

    result = run_search(DFS(), grid)

    assert result.path == []
    assert result.visited == {(0, 0), (0, 1), (1, 0), (1, 1)}
    assert result.nodes_expanded == 4
