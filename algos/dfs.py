from algos.search_algo import SearchAlgorith
from grid import STATIC_WALLS, TRESURE, TRAP


class DFS(SearchAlgorith):

    #DOWN,RIGHT,UP,LEFT
    DIRECTIONS = [[1,0],[0,1],[-1,0],[0,-1]]
    AVOID = {TRAP, STATIC_WALLS}

    def search(self, grid, startr, startc):
        n = len(grid)
        m = len(grid[0])

        stack = [(startr, startc)]
        seen = {(startr, startc): (-1, -1)}
        treasure_loc = ()

        while stack:
            current_r, current_c = stack.pop()

            if grid[current_r][current_c] == TRESURE:
                treasure_loc = (current_r, current_c)
                break

            for dr, dc in self.DIRECTIONS:
                if (0 <= (current_r + dr) < n and 0 <= (current_c + dc) < m and 
                    (current_r + dr, current_c + dc) not in seen and
                      grid[current_r + dr][current_c + dc] not in self.AVOID):
                    
                    stack.append((current_r + dr, current_c + dc))
                    seen[(current_r + dr, current_c + dc)] = (current_r, current_c)

        return seen, treasure_loc