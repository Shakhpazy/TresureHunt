import heapq
from algos.search_algo import SearchAlgorith
from grid import STATIC_WALLS, TREASURE, TRAP, START


class UCS(SearchAlgorith):

    #DOWN,RIGHT,UP,LEFT
    DIRECTIONS = [[1,0],[0,1],[-1,0],[0,-1]]
    AVOID = {TRAP, STATIC_WALLS}

    def __init__(self, weights):
        self.weights = weights

    def _validate(self, grid, startr, startc):
        if len(self.weights) != len(grid) or any(len(w) != len(g) for w, g in zip(self.weights, grid)):
            raise ValueError("Weight matrix must be the same size as the grid.")

        for r in range(len(grid)):
            for c in range(len(grid[0])):
                weight = self.weights[r][c]

                # a mismatch here means the weights belong to a different map
                if (grid[r][c] in self.AVOID) != (weight is None):
                    raise ValueError(f"Weights do not match the grid at {(r, c)}.")
                if grid[r][c] == START:
                    if weight != 0:
                        raise ValueError(f"The start cell must cost 0, got {weight}.")
                elif weight is not None and weight < 1:
                    raise ValueError(f"Weight at {(r, c)} must be at least 1, got {weight}.")

        if grid[startr][startc] != START:
            raise ValueError(f"No start cell at {(startr, startc)}.")

    def search(self, grid, startr, startc):
        self._validate(grid, startr, startc)
        n = len(grid)
        m = len(grid[0])

        # each entry is (total cost so far, row, col, parent); a cell is only
        # marked seen when popped, since a cheaper route can still reach it
        priority_que = [(0, startr, startc, (-1, -1))]
        seen = {}
        treasure_loc = ()
        total_cost = None

        while priority_que:
            cost, current_r, current_c, parent = heapq.heappop(priority_que)

            # stale entry: a cheaper route to this cell was already popped
            if (current_r, current_c) in seen:
                continue

            seen[(current_r, current_c)] = parent

            if grid[current_r][current_c] == TREASURE:
                treasure_loc = (current_r, current_c)
                total_cost = cost
                break

            for dr, dc in self.DIRECTIONS:
                next_r, next_c = current_r + dr, current_c + dc
                if (0 <= next_r < n and 0 <= next_c < m and
                    (next_r, next_c) not in seen and
                    grid[next_r][next_c] not in self.AVOID):

                    heapq.heappush(priority_que,
                                   (cost + self.weights[next_r][next_c], next_r, next_c, (current_r, current_c)))

        return seen, treasure_loc, total_cost
