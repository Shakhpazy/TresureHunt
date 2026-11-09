import random

import pytest

from algos.astar import ASTAR
from algos.bfs import BFS
from algos.dfs import DFS
from algos.ucs import UCS
from grid import EMPTY, START, STATIC_WALLS, TRAP, TREASURE, TreasureMap, create_weight_matrix
from helpers import make_grid, run_search


def test_main_grid_weight_matrix_gives_traps_no_weight_like_walls():
    grid = make_grid("S#XT")

    assert create_weight_matrix(grid) == [[0, None, None, 1]]


def test_custom_grid_weight_matrix_keeps_the_trap_cost_when_passable():
    grid = make_grid("S#XT")

    assert create_weight_matrix(grid, traps_passable=True) == [[0, None, 6, 1]]


@pytest.mark.parametrize("make_algo", [
    lambda grid: DFS(),
    lambda grid: BFS(),
    lambda grid: UCS(create_weight_matrix(grid)),
    lambda grid: ASTAR(create_weight_matrix(grid)),
])
def test_every_algorithm_reports_no_path_when_a_trap_blocks_the_only_way(make_algo):
    grid = make_grid("SXT")

    result = run_search(make_algo(grid), grid)

    assert result.path == []


@pytest.mark.parametrize("make_algo", [
    lambda grid: DFS(),
    lambda grid: BFS(),
    lambda grid: UCS(create_weight_matrix(grid)),
    lambda grid: ASTAR(create_weight_matrix(grid)),
])
def test_no_algorithm_ever_enters_a_trap_on_random_main_grids(make_algo):
    rng = random.Random(11)
    random.seed(11)  # TreasureMap uses the global random
    for _ in range(300):
        grid = TreasureMap(10, 15).getMap()

        result = run_search(make_algo(grid), grid)

        assert not any(grid[r][c] == TRAP for r, c in result.path)
        assert not any(grid[r][c] == TRAP for r, c in result.visited)
