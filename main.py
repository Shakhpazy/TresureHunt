import random

from grid import TreasureMap
from gui import Gui
from agents import Agent
from algos.dfs import DFS
from algos.bfs import BFS
from gui import ALGORITHMS

GRID_SIZE = 10
STATIC_WALL_RATIO = 0.15


def create_random_map():
    size = GRID_SIZE
    static_walls = round(size * size * STATIC_WALL_RATIO)
    return TreasureMap(size, static_walls).getMap()


def run_current_algorithm():
    current_algo = None

    if gui.current_algo_idx == 0:
        current_algo = DFS()
    else:
        current_algo = BFS()

    visited, solution, execution_time = agent.run(current_algo)
    gui.set_solution_path(solution)
    gui.set_visited(visited)
    print(solution)
    print(f"{ALGORITHMS[gui.current_algo_idx]} took {execution_time:.6f} seconds")
    return visited, solution


def regenerate_map():
    new_grid = create_random_map()
    agent.setGrid(new_grid)
    return new_grid


grid = create_random_map()
agent = Agent(grid)
gui = Gui(grid, regenerate_map, run_current_algorithm)

gui.run()
