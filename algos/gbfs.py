import heapq

from algos.search_algo import SearchAlgorith
from grid import START, STATIC_WALLS, TREASURE, TRAP


class GBFS(SearchAlgorith):
    """Greedy best-first search: always expand the cell that LOOKS closest.

    It orders its frontier by h only, the Manhattan distance to the nearest
    treasure. It never looks at how far it has already walked, so it is fast
    but does not promise the shortest path.
    """

    # DOWN, RIGHT, UP, LEFT
    DIRECTIONS = [[1, 0], [0, 1], [-1, 0], [0, -1]]
    AVOID = {TRAP, STATIC_WALLS}

    def _priority(self, row, col):
        # smaller is expanded first: closest-looking cell, then the smaller
        # row + col, then the smaller row. The last two make ties deterministic.
        h = min(abs(row - r) + abs(col - c) for r, c in self.treasures)
        return (h, row + col, row)

    def search(self, grid, startr, startc):
        rows = len(grid)
        cols = len(grid[0])

        if grid[startr][startc] != START:
            raise ValueError(f"No start cell at {(startr, startc)}.")
        self.treasures = [
            (r, c) for r in range(rows) for c in range(cols) if grid[r][c] == TREASURE
        ]
        if not self.treasures:
            raise ValueError("No treasure on the grid.")

        # a cell is marked seen when it is first queued (like BFS), which is
        # also when its parent is recorded. Its priority depends only on the
        # cell, so queueing it again later could never change its place.
        seen = {(startr, startc): (-1, -1)}
        heap = [(*self._priority(startr, startc), startr, startc)]
        nodes_expanded = 0

        while heap:
            *_, current_r, current_c = heapq.heappop(heap)
            nodes_expanded += 1

            if grid[current_r][current_c] == TREASURE:
                return seen, (current_r, current_c), nodes_expanded

            for dr, dc in self.DIRECTIONS:
                next_r, next_c = current_r + dr, current_c + dc
                if (0 <= next_r < rows and 0 <= next_c < cols
                        and (next_r, next_c) not in seen
                        and grid[next_r][next_c] not in self.AVOID):
                    seen[(next_r, next_c)] = (current_r, current_c)
                    heapq.heappush(heap, (*self._priority(next_r, next_c), next_r, next_c))

        return seen, (), nodes_expanded
