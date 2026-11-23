import pytest

from agents import Agent
from algos.astar import ASTAR
from algos.bfs import BFS
from algos.dfs import DFS
from algos.gbfs import GBFS
from algos.ucs import UCS
from grid import create_weight_matrix
from helpers import assert_valid_path, make_grid
from report import format_run_report


ALGORITHMS = [DFS, BFS, ASTAR, GBFS, lambda: UCS([[1, 1, 0, 1, 1, 1]])]


@pytest.mark.parametrize("make_algo", ALGORITHMS)
def test_agent_returns_separate_paths_to_every_treasure(make_algo):
    grid = make_grid("T.S..T")
    before = [row[:] for row in grid]
    algo = make_algo()
    _, paths, _, cost, _ = Agent(grid).run(algo)

    assert {path[-1] for path in paths} == {(0, 0), (0, 5)}
    assert len(paths) == 2
    for path in paths:
        assert_valid_path(grid, path)
    if isinstance(algo, (ASTAR, UCS)):
        assert cost == 5  # 2 steps to the left, 3 to the right
    assert grid == before
    assert Agent(grid).run(algo)[1] == paths


@pytest.mark.parametrize("algorithm", [DFS, BFS, ASTAR, GBFS, UCS])
def test_agent_keeps_reachable_paths_when_another_treasure_is_blocked(algorithm):
    grid = make_grid("S.T#T")
    algo = algorithm(create_weight_matrix(grid)) if algorithm is UCS else algorithm()
    _, paths, _, cost, _ = Agent(grid).run(algo)
    assert paths == [[(0, 0), (0, 1), (0, 2)]]
    if algorithm in (ASTAR, UCS):
        assert cost == 2


@pytest.mark.parametrize("algorithm", [DFS, BFS, ASTAR, GBFS, UCS])
def test_agent_all_treasure_paths_still_avoid_traps(algorithm):
    grid = make_grid("SXT", "...", "T..")
    algo = algorithm(create_weight_matrix(grid)) if algorithm is UCS else algorithm()
    _, paths, _, _, _ = Agent(grid).run(algo)
    assert len(paths) == 2
    for path in paths:
        assert_valid_path(grid, path)


def test_weighted_report_total_matches_both_path_trails():
    grid = make_grid("T.S..T")
    weights = [[1, 4, 0, 2, 3, 1]]
    _, paths, elapsed, cost, nodes = Agent(grid).run(UCS(weights))
    assert cost == 11
    report = format_run_report("UCS", paths, nodes, elapsed, cost, weights)
    assert "Path to treasure 2:" in report
    assert "Path cost: 11" in report
