import time
from algos.search_algo import SearchAlgorith
from grid import START


class Agent:

    def __init__(self, grid) -> None:
        self.setGrid(grid)

    def setGrid(self, grid):
        if not grid or not grid[0]:
            raise ValueError("Grid is empty or missing rows/columns.")
        self.grid = grid

        self.startr = 0
        self.startc = 0

        self.setStart(self.grid)

    def setStart(self, grid):
        for r in range(len(grid)):
            for c in range(len(grid[0])):
                if grid[r][c] == START:
                    self.startr = r
                    self.startc = c

    def run(self, algo : SearchAlgorith):
        start_time = time.perf_counter()

        result = algo.search(self.grid, self.startr, self.startc)

        execution_time = time.perf_counter() - start_time

        return result, execution_time