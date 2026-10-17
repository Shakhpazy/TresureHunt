import random

STATIC_WALLS = "#"
TRESURE = "T"
TRAP = "X"
EMPTY = ""

class TresureMap:


    def __init__(self, size, staticWalls=1):
        if size <= 2:
            raise ValueError(size, "Size must be greater than 2")
        if staticWalls < 0:
            raise ValueError(staticWalls, "walls must be greater that -1")
        if staticWalls > size * size - 2:
            raise ValueError("There must be room for the treasure and trap")
        
        self.size = size
        self.staticWalls = staticWalls
        self.tresuremap = self.createNewMap(self.size)

    def getMap(self):
        return self.tresuremap
    
    def createNewMap(self, size: int):
        map = [[EMPTY for _ in range(size)] for _ in range(size)]

        self.placeItem(map, self.staticWalls, STATIC_WALLS)
        self.placeItem(map, 1, TRESURE)
        self.placeItem(map, 1, TRAP)

        return map


    def placeItem(self, map, place, type):
        current = 0
        while (current < place):
               row, col = self.generateRandomPosition()
               if map[row][col] == EMPTY:
                   map[row][col] = type
                   current += 1
        

    def generateRandomPosition(self):
        row = random.randint(0, self.size-1)
        col = random.randint(0, self.size-1)
        return row, col


    