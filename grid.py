import random

STATIC_WALLS = "#"
TRESURE = "T"
TRAP = "X"
EMPTY = ""
START = "S"

class TresureMap:


    def __init__(self, size, staticWalls=1):
        if size < 8:
            raise ValueError(size, "Size must be greater than 7")
        if staticWalls < 1 :
            raise ValueError(staticWalls, "Walls must be greater than 1")
        if staticWalls > size * size - 2:
            raise ValueError("There must be room for the treasure and trap")
        
        self.size = size
        self.staticWalls = staticWalls
        self.tresuremap = self.createNewMap(self.size)

    def getMap(self):
        return self.tresuremap
    
    def createNewMap(self, size: int):
        my_map = [[EMPTY for _ in range(size)] for _ in range(size)]

        self.placeItem(my_map, self.staticWalls, STATIC_WALLS)
        self.placeItem(my_map, 1, TRESURE)
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


    