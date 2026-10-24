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

    def _getSolutionPath(self, visited, treasure_loc):
        if not treasure_loc:
            return []
        
        path = []
        current = treasure_loc

        while current != (-1, -1):
            path.append(current)
            current = visited.get(current, (-1, -1))

        return path[::-1]

    def _getVisitedLocs(self, visited):
        return list(visited.keys())

    def run(self, algo : SearchAlgorith):
        start_time = time.perf_counter()

        visited, treasure_loc = algo.search(self.grid, self.startr, self.startc)

        execution_time = time.perf_counter() - start_time

        #return a list of solution path, return a list of all paths, return executiontime
        solution_path = self._getSolutionPath(visited, treasure_loc)
        visited_loc = self._getVisitedLocs(visited)

        return visited_loc, solution_path, execution_time