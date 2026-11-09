import random

from grid import TreasureMap, create_weight_matrix
from gui import Gui
from agents import Agent
from algos.dfs import DFS
from algos.bfs import BFS
from algos.ucs import UCS
from algos.astar import ASTAR
from algos.gbfs import GBFS
from report import format_run_report
from gui import ALGORITHMS
from custom_grids import load_custom_grids

GRID_SIZE = 20
STATIC_WALL_RATIO = 0.15

# only exists while a weighted algorithm is selected
weights = None
# True only while a custom grid is loaded. On the random map traps are walls for
# every algorithm and only UCS has weights (random). Custom grids are unchanged:
# traps stay passable for UCS and A*, and both use the constant weight matrix.
traps_passable = False
custom_grids = load_custom_grids()


def create_random_map():
    size = GRID_SIZE
    static_walls = round(size * size * STATIC_WALL_RATIO)
    return TreasureMap(size, static_walls).getMap()


def uses_weights(algo_name):
    # UCS always; A* only on custom grids (on the random map it costs 1 per step).
    # DFS, BFS and GBFS never use weights.
    return algo_name == "UCS" or (algo_name == "A*" and traps_passable)


def refresh_weights():
    # a fresh matrix for the algorithms that use one; random only on the random map
    global weights

    if uses_weights(ALGORITHMS[gui.current_algo_idx]):
        weights = create_weight_matrix(
            agent.grid, traps_passable, random_weights=not traps_passable
        )
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
        current_algo = UCS(weights, unusual_costs=traps_passable)
    elif algo_name == "A*":
        if uses_weights(algo_name) and weights is None:
            refresh_weights()
        current_algo = ASTAR(weights, unusual_costs=traps_passable)
    elif algo_name == "GBFS":
        current_algo = GBFS()
    else:
        raise ValueError(f"Unknown algorithm: {algo_name}")

    visited, solution, execution_time, total_cost, nodes_expanded = agent.run(current_algo)
    gui.set_solution_path(solution)
    gui.set_visited(visited)

    if total_cost is None: #Quick Fix
        total_cost = len(solution) - 1 if solution else 0
    gui.show_info(total_cost, nodes_expanded, execution_time)

    print(format_run_report(
        algo_name, solution, nodes_expanded, execution_time, total_cost,
        weights if uses_weights(algo_name) else None,
    ))
    return visited, solution


def regenerate_map():
    global traps_passable
    traps_passable = False  # before refresh_weights, which reads it
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


def select_custom_grid(index):
    global traps_passable
    traps_passable = True  # before refresh_weights, which reads it
    new_grid = custom_grids[index][1]
    agent.setGrid(new_grid)
    refresh_weights()
    return new_grid

grid = create_random_map()
agent = Agent(grid)
gui = Gui(
    grid,
    regenerate_map,
    run_current_algorithm,
    on_algo_change=algorithm_changed,
    custom_grid_names=[name for name, _ in custom_grids],
    on_custom_grid=select_custom_grid,
)


gui.run()
