import random

from grid import TresureMap
from gui import Gui

MIN_GRID_SIZE = 8
MAX_GRID_SIZE = 16
STATIC_WALL_RATIO = 0.15


def create_random_map():
    size = random.randint(MIN_GRID_SIZE, MAX_GRID_SIZE)
    static_walls = round(size * size * STATIC_WALL_RATIO)
    return TresureMap(size, static_walls).getMap()


gui = Gui(create_random_map())
gui.run()
