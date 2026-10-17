from grid import TresureMap
from gui import Gui

game = TresureMap(8, 2)
current = game.getMap()

print(current)

gui = Gui(current)
gui.run()
