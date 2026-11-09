import heapq


from algos.search_algo import SearchAlgorith
from grid import START, STATIC_WALLS, TREASURE, TRAP, TRAP_COST


class ASTAR(SearchAlgorith):
    # DOWN, RIGHT, UP, LEFT
    DIRECTIONS = [[1, 0], [0, 1], [-1, 0], [0, -1]]
    AVOID = {TRAP, STATIC_WALLS}

    def __init__(self, weights=None, unusual_costs=False):
        self.weights = weights
        # filled in by search(): every treasure cell on the grid it is given
        self.treasures = []
        self.unusual_costs = unusual_costs
        self.avoid = {STATIC_WALLS} if unusual_costs else self.AVOID

    def _validate(self, grid, startr, startc):
        rows = len(grid)
        cols = len(grid[0])

        # the grid is the only source of truth for where the treasures are
        self.treasures = [
            (r, c) for r in range(rows) for c in range(cols) if grid[r][c] == TREASURE
        ]
        if not self.treasures:
            raise ValueError("No treasure on the grid.")
        if grid[startr][startc] != START:
            raise ValueError(f"No start cell at {(startr, startc)}.")

        if self.weights is None:
            return
        if len(self.weights) != rows or any(
            len(weight_row) != len(grid_row)
            for weight_row, grid_row in zip(self.weights, grid)
        ):
            raise ValueError("Weight matrix must be the same size as the grid.")

        for r in range(rows):
            for c in range(cols):
                cell = grid[r][c]
                weight = self.weights[r][c]
                if cell == STATIC_WALLS and weight is not None:
                    raise ValueError(f"Weights do not match the grid at {(r, c)}.")
                if cell == TRAP:
                    if self.unusual_costs and weight != TRAP_COST:
                        raise ValueError(f"Trap weight at {(r, c)} must be {TRAP_COST}.")
                    if not self.unusual_costs and weight is not None:
                        raise ValueError(f"Trap at {(r, c)} is blocked, so it cannot have a weight.")
                if cell not in (STATIC_WALLS, TRAP) and weight is None:
                    raise ValueError(f"Weights do not match the grid at {(r, c)}.")
                if cell == START:
                    if weight < 0:
                        raise ValueError("Start weight must be at least 0.")
                elif weight is not None and weight < 1:
                    raise ValueError(f"Weight at {(r, c)} must be at least 1.")

    def _heuristic(self, row, col):
        # distance to the NEAREST treasure: never overestimates the cost to
        # the closest goal, and is 0 on every treasure cell
        return min(abs(row - r) + abs(col - c) for r, c in self.treasures)

    def _step_cost(self, grid, row, col):
        if grid[row][col] == TRAP:
            return TRAP_COST
        if self.weights is not None:
            return self.weights[row][col]
        return 1

    def search(self, grid, startr, startc):
        self._validate(grid, startr, startc)
        rows = len(grid)
        cols = len(grid[0])
        start = (startr, startc)
        start_cost = (
            self.weights[startr][startc]
            if self.weights is not None and self.unusual_costs
            else 0
        )

        costs = {start: start_cost}
        seen = {start: (-1, -1)}
        expanded = set()
        heap = [(start_cost + self._heuristic(*start), start_cost, startr, startc)]

        while heap:
            _, current_cost, current_r, current_c = heapq.heappop(heap)
            current = (current_r, current_c)

            if current_cost != costs.get(current) or current in expanded:
                continue

            expanded.add(current)
            if grid[current_r][current_c] == TREASURE:
                return seen, current, len(expanded), current_cost

            for dr, dc in self.DIRECTIONS:
                next_r, next_c = current_r + dr, current_c + dc
                if not (0 <= next_r < rows and 0 <= next_c < cols):
                    continue
                if grid[next_r][next_c] in self.avoid:
                    continue

                next_cell = (next_r, next_c)
                new_cost = current_cost + self._step_cost(grid, next_r, next_c)
                if new_cost >= costs.get(next_cell, float("inf")):
                    continue

                costs[next_cell] = new_cost
                seen[next_cell] = current
                priority = new_cost + self._heuristic(next_r, next_c)
                heapq.heappush(heap, (priority, new_cost, next_r, next_c))

        return seen, (), len(expanded), None

