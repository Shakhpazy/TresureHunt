import heapq
from algos.search_algo import SearchAlgorith
from grid import STATIC_WALLS, TREASURE, TRAP, START, TRAP_COST


class UCS(SearchAlgorith):

    #DOWN,RIGHT,UP,LEFT
    DIRECTIONS = [[1,0],[0,1],[-1,0],[0,-1]]
    AVOID = {TRAP, STATIC_WALLS}

    def __init__(self, weights, unusual_costs=False):
        # unusual_costs=False (default): traps are blocked and have no weight.
        # unusual_costs=True: traps can be walked through at TRAP_COST, and the
        # start cell's own weight counts toward the total instead of having to be 0
        self.weights = weights
        self.unusual_costs = unusual_costs
        self.avoid = {STATIC_WALLS} if unusual_costs else self.AVOID

    def _validate(self, grid, startr, startc):
        if len(self.weights) != len(grid) or any(len(w) != len(g) for w, g in zip(self.weights, grid)):
            raise ValueError("Weight matrix must be the same size as the grid.")

        for r in range(len(grid)):
            for c in range(len(grid[0])):
                weight = self.weights[r][c]

                # Walls never have a cost. Traps always have their fixed cost,
                # even when this search is configured not to enter them.
                if grid[r][c] == STATIC_WALLS and weight is not None:
                    raise ValueError(f"Weights do not match the grid at {(r, c)}.")
                if grid[r][c] == TRAP:
                    if self.unusual_costs and weight != TRAP_COST:
                        raise ValueError(f"Trap weight at {(r, c)} must be {TRAP_COST}.")
                    if not self.unusual_costs and weight is not None:
                        raise ValueError(f"Trap at {(r, c)} is blocked, so it cannot have a weight.")
                if grid[r][c] not in (STATIC_WALLS, TRAP) and weight is None:
                    raise ValueError(f"Weights do not match the grid at {(r, c)}.")
                if grid[r][c] == START:
                    if not self.unusual_costs and weight != 0:
                        raise ValueError(f"The start cell must cost 0, got {weight}.")
                    if self.unusual_costs and weight < 0:
                        raise ValueError(f"The start cell cannot have a negative cost, got {weight}.")
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
        start_cost = self.weights[startr][startc] if self.unusual_costs else 0
        priority_que = [(start_cost, startr, startc, (-1, -1))]
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
                    grid[next_r][next_c] not in self.avoid):

                    heapq.heappush(priority_que,
                                   (cost + self.weights[next_r][next_c], next_r, next_c, (current_r, current_c)))

        # UCS marks a cell seen only when popped, so every seen cell was expanded
        return seen, treasure_loc, len(seen), total_cost
