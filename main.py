import random

from grid import TREASURE, TreasureMap, create_weight_matrix
from gui import Gui
from agents import Agent
from algos.dfs import DFS
from algos.bfs import BFS
from algos.ucs import UCS
from algos.astar import ASTAR
from report import format_run_report
from gui import ALGORITHMS
from custom_grids import load_custom_grids

GRID_SIZE = 30
STATIC_WALL_RATIO = 0.15

# only exists while a weighted algorithm is selected
weights = None
custom_grids = load_custom_grids()


def create_random_map():
    size = GRID_SIZE
    static_walls = round(size * size * STATIC_WALL_RATIO)
    return TreasureMap(size, static_walls).getMap()


def refresh_weights():
    # UCS and A* get a fresh weight matrix; DFS and BFS do not use one.
    global weights

    if ALGORITHMS[gui.current_algo_idx] in ("UCS", "A*"):
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
    elif algo_name == "A*":
        if weights is None:
            refresh_weights()
        treasure_row, treasure_col = next(
            (r, c)
            for r, row in enumerate(agent.grid)
            for c, cell in enumerate(row)
            if cell == TREASURE
        )
        current_algo = ASTAR(
            weights,
            unusual_costs=True,
            treasure_loc_row=treasure_row,
            treasure_loc_col=treasure_col,
        )
    else:
        raise ValueError(f"Unknown algorithm: {algo_name}")

    visited, solution, execution_time, total_cost, nodes_expanded = agent.run(current_algo)
    gui.set_solution_path(solution)
    gui.set_visited(visited)
    print(format_run_report(
        algo_name, solution, nodes_expanded, execution_time, total_cost,
        weights if algo_name in ("UCS", "A*") else None,
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


def select_custom_grid(index):
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
