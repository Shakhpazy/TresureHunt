from algos.search_algo import SearchAlgorith
from grid import STATIC_WALLS, TRESURE, TRAP
from collections import deque


class BFS(SearchAlgorith):

    #DOWN,RIGHT,UP,LEFT
    DIRECTIONS = [[1,0],[0,1],[-1,0],[0,-1]]
    AVOID = {TRAP, STATIC_WALLS}

    def search(self, grid, startr, startc):
        n = len(grid)
        m = len(grid[0])

        que = deque([(startr, startc)])
        seen = {(startr, startc): (-1, -1)}
        treasure_loc = ()
        found = False
        while que and not found:
            for i in range(len(que)):
                current_r, current_c = que.popleft()

                if grid[current_r][current_c] == TRESURE:
                    treasure_loc = (current_r, current_c)
                    found = True
                    break

                for dr, dc in self.DIRECTIONS:
                    if (0 <= (current_r + dr) < n and 0 <= (current_c + dc) < m and 
                        (current_r + dr, current_c + dc) not in seen and
                        grid[current_r + dr][current_c + dc] not in self.AVOID):

                        que.append((current_r + dr, current_c + dc))
                        seen[(current_r + dr, current_c + dc)] = (current_r, current_c)

        return seen, treasure_loc