import random

from grid import TresureMap
from gui import Gui
from agents import Agent
from algos.dfs import DFS

MIN_GRID_SIZE = 8
MAX_GRID_SIZE = 16
STATIC_WALL_RATIO = 0.15


def create_random_map():
    size = random.randint(MIN_GRID_SIZE, MAX_GRID_SIZE)
    static_walls = round(size * size * STATIC_WALL_RATIO)
    return TresureMap(size, static_walls).getMap()


def regenerate_map():
    new_grid = create_random_map()
    agent.setGrid(new_grid)
    visited, solution, execution_time = agent.run(DFS())
    gui.set_solution_path(solution)
    gui.set_visited(visited)    
    return new_grid


grid = create_random_map()
agent = Agent(grid)
gui = Gui(grid, regenerate_map)

visited, solution, execution_time = agent.run(DFS())
gui.set_solution_path(solution)
gui.set_visited(visited)

gui.run()
