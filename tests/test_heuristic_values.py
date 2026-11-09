import random

import pytest

from algos.astar import ASTAR
from algos.bfs import BFS
from algos.dfs import DFS
from algos.gbfs import GBFS
from algos.ucs import UCS
from agents import Agent
from grid import TREASURE, TreasureMap, create_weight_matrix
from helpers import make_grid
from report import format_run_report


def nearest_treasure_distance(grid, row, col):
    return min(
        abs(row - r) + abs(col - c)
        for r, line in enumerate(grid) for c, cell in enumerate(line) if cell == TREASURE
    )


@pytest.mark.parametrize("make_algo", [lambda: ASTAR(), lambda: GBFS()])
def test_one_value_per_expanded_cell_each_equal_to_h_and_zero_at_the_treasure(make_algo):
    random.seed(435)
    for _ in range(300):
        grid = TreasureMap(12, 25).getMap()
        algo = make_algo()

        _, solution, _, _, nodes_expanded = Agent(grid).run(algo)

        assert len(algo.heuristic_values) == nodes_expanded
        for (row, col), h in algo.heuristic_values:
            assert h == nearest_treasure_distance(grid, row, col)
        if solution:
            assert algo.heuristic_values[-1][1] == 0       # the treasure is expanded last
            assert algo.heuristic_values[-1][0] == solution[-1]


@pytest.mark.parametrize("make_algo", [lambda: ASTAR(), lambda: GBFS()])
def test_values_are_still_reported_when_there_is_no_path(make_algo):
    grid = make_grid("S#T")
    algo = make_algo()

    _, solution, _, _, nodes_expanded = Agent(grid).run(algo)

    assert solution == []
    assert algo.heuristic_values == [((0, 0), 2)]
    assert nodes_expanded == 1


@pytest.mark.parametrize("make_algo", [lambda: ASTAR(), lambda: GBFS()])
def test_a_reused_instance_does_not_accumulate_old_values(make_algo):
    grid = make_grid("S.T")
    algo = make_algo()

    Agent(grid).run(algo)
    first = list(algo.heuristic_values)
    Agent(grid).run(algo)

    assert algo.heuristic_values == first == [((0, 0), 2), ((0, 1), 1), ((0, 2), 0)]


@pytest.mark.parametrize("make_algo", [
    lambda grid: DFS(),
    lambda grid: BFS(),
    lambda grid: UCS(create_weight_matrix(grid)),
])
def test_searches_without_a_heuristic_have_no_heuristic_values(make_algo):
    grid = make_grid("S.T")
    algo = make_algo(grid)

    Agent(grid).run(algo)

    assert algo.heuristic_values is None


def test_report_lists_every_value_then_the_sum_before_the_path_cost():
    report = format_run_report(
        "GBFS", [(0, 0), (0, 1)], 2, 0.001, 1, None,
        [((0, 0), 1), ((0, 1), 0)],
    ).splitlines()

    assert report[-6:] == [
        "h(0, 0) = 1",
        "h(0, 1) = 0",
        "Heuristic values: 1",
        "Path cost: 1",
        "Nodes expanded: 2",
        "Runtime: 0.001000 seconds",
    ]


def test_report_has_no_heuristic_lines_for_searches_without_one():
    report = format_run_report("BFS", [(0, 0), (0, 1)], 2, 0.001, 1, None, None)

    assert "Heuristic" not in report and "h(" not in report


def test_report_still_lists_the_values_when_there_is_no_path():
    report = format_run_report("A*", [], 1, 0.001, None, None, [((0, 0), 2)])

    assert "No path to the treasure" in report
    assert "h(0, 0) = 2" in report and "Heuristic values: 2" in report
