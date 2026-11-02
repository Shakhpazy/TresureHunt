import random

STATIC_WALLS = "#"
TREASURE = "T"
TRAP = "X"
EMPTY = ""
START = "S"

MIN_WEIGHT = 1
MAX_WEIGHT = 99

class TreasureMap:


    def __init__(self, size, staticWalls=1):
        if size != 10:
            raise ValueError(size, "Size must always be 10*10")
        if staticWalls < 1 :
            raise ValueError(staticWalls, "Walls must be greater than 1")
        if staticWalls > size * size - 2:
            raise ValueError("There must be room for the treasure and trap")
        
        self.size = size
        self.staticWalls = staticWalls
        self.treasuremap = self.createNewMap(self.size)

    def getMap(self):
        return self.treasuremap
    
    def createNewMap(self, size: int):
        my_map = [[EMPTY for _ in range(size)] for _ in range(size)]

        self.placeItem(my_map, self.staticWalls, STATIC_WALLS)
        self.placeItem(my_map, 1, TREASURE)
        self.placeItem(my_map, 1, TRAP)
        self.placeItem(my_map, 1, START)

        return my_map


    def placeItem(self, the_map, item_amount, item_type):
        current = 0
        while (current < item_amount):
               row, col = self.generateRandomPosition()
               if the_map[row][col] == EMPTY:
                   the_map[row][col] = item_type
                   current += 1
        

    def generateRandomPosition(self):
        row = random.randint(0, self.size-1)
        col = random.randint(0, self.size-1)
        return row, col


def create_weight_matrix(grid):
    """Cost of stepping onto each cell of grid, used only by uniform cost search.

    Walls and traps are None (impassable), the start is 0 (never stepped onto),
    and empty cells and the treasure get a random weight.
    """
    weights = []
    for row in grid:
        weight_row = []
        for cell in row:
            if cell in (STATIC_WALLS, TRAP):
                weight_row.append(None)
            elif cell == START:
                weight_row.append(0)
            else:
                weight_row.append(random.randint(MIN_WEIGHT, MAX_WEIGHT))
        weights.append(weight_row)
    return weights
