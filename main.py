import random

from grid import TreasureMap, create_weight_matrix
from gui import Gui
from agents import Agent
from algos.dfs import DFS
from algos.bfs import BFS
from algos.ucs import UCS
from report import format_run_report
from gui import ALGORITHMS

GRID_SIZE = 10
STATIC_WALL_RATIO = 0.15

# only exists while UCS is the selected algorithm
weights = None


def create_random_map():
    size = GRID_SIZE
    static_walls = round(size * size * STATIC_WALL_RATIO)
    return TreasureMap(size, static_walls).getMap()


def refresh_weights():
    # UCS gets a fresh weight matrix over the current map, the other searches don't use one
    global weights

    if ALGORITHMS[gui.current_algo_idx] == "UCS":
        weights = create_weight_matrix(agent.grid)
    else:
        weights = None
    gui.set_weights(weights)


def run_current_algorithm():
    algo_name = ALGORITHMS[gui.current_algo_idx]

    if algo_name == "DFS":
        current_algo = DFS()
    elif algo_name == "BFS":
        current_algo = BFS()
    elif algo_name == "UCS":
        if weights is None:
            refresh_weights()
        current_algo = UCS(weights)
    else:
        raise ValueError(f"Unknown algorithm: {algo_name}")

    visited, solution, execution_time, total_cost, nodes_expanded = agent.run(current_algo)
    gui.set_solution_path(solution)
    gui.set_visited(visited)
    print(format_run_report(
        algo_name, solution, nodes_expanded, execution_time, total_cost,
        weights if algo_name == "UCS" else None,
    ))
    return visited, solution


def regenerate_map():
    new_grid = create_random_map()
    agent.setGrid(new_grid)
    refresh_weights()
    return new_grid


def algorithm_changed():
    refresh_weights()
    if weights is not None:
        # the old overlay was drawn for a different weight matrix
        gui.set_visited([])
        gui.set_solution_path([])


grid = create_random_map()
agent = Agent(grid)
gui = Gui(grid, regenerate_map, run_current_algorithm, on_algo_change=algorithm_changed)

gui.run()
