from algos.search_algo import SearchAlgorith
from grid import STATIC_WALLS, TREASURE, TRAP


class DFS(SearchAlgorith):

    #DOWN,RIGHT,UP,LEFT
    DIRECTIONS = [[1,0],[0,1],[-1,0],[0,-1]]
    AVOID = {TRAP, STATIC_WALLS}

    def search(self, grid, startr, startc):
        n = len(grid)
        m = len(grid[0])

        # each entry is (cell, parent); a cell is only marked seen when popped
        stack = [((startr, startc), (-1, -1))]
        seen = {}
        treasure_loc = ()

        while stack:
            (current_r, current_c), parent = stack.pop()

            # the same cell can be on the stack more than once
            if (current_r, current_c) in seen:
                continue

            seen[(current_r, current_c)] = parent

            if grid[current_r][current_c] == TREASURE:
                treasure_loc = (current_r, current_c)
                break

            for dr, dc in self.DIRECTIONS:
                if (0 <= (current_r + dr) < n and 0 <= (current_c + dc) < m and
                    (current_r + dr, current_c + dc) not in seen and
                      grid[current_r + dr][current_c + dc] not in self.AVOID):

                    stack.append(((current_r + dr, current_c + dc), (current_r, current_c)))

        # DFS marks a cell seen only when popped, so every seen cell was expanded
        return seen, treasure_loc, len(seen)