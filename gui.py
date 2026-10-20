import pygame
from grid import STATIC_WALLS, TRESURE, TRAP

CELL_SIZE = 40
BACKGROUND_COLOR = (255, 255, 255)
GRID_COLOR = (0, 0, 0)
WALL_BACKGROUND = (255, 220, 0)
TREASURE_BACKGROUND = (255, 170, 200)
TRAP_BACKGROUND = (0, 220, 220)
WALL_TEXT_COLOR = (0, 0, 0)
TREASURE_TEXT_COLOR = (0, 140, 0)
TRAP_TEXT_COLOR = (220, 0, 0)

class Gui:

    def __init__(self, grid, show_grid_lines=True):
        if not grid:
            raise ValueError("2d matrix of size 8x8 or more should be inserted", grid)

        pygame.init()
        self.grid = grid
        self.show_grid_lines = show_grid_lines
        self.font = pygame.font.Font(None, 32)
        self.screen = pygame.display.set_mode((CELL_SIZE*len(grid[0]),CELL_SIZE*len(grid)))
        pygame.display.set_caption("Treasure Hunt")

    def draw_grid(self):
        self.screen.fill(BACKGROUND_COLOR)

        for row in range(len(self.grid)):
            for col in range(len(self.grid[row])):
                rectangle = pygame.Rect(
                    col * CELL_SIZE,
                    row * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE,
                )

                cell = self.grid[row][col]
                cell_background = BACKGROUND_COLOR
                symbol = ""
                symbol_color = GRID_COLOR

                if cell == STATIC_WALLS:
                    cell_background = WALL_BACKGROUND
                    symbol = "#"
                    symbol_color = WALL_TEXT_COLOR
                elif cell == TRESURE:
                    cell_background = TREASURE_BACKGROUND
                    symbol = "T"
                    symbol_color = TREASURE_TEXT_COLOR
                elif cell == TRAP:
                    cell_background = TRAP_BACKGROUND
                    symbol = "X"
                    symbol_color = TRAP_TEXT_COLOR

                pygame.draw.rect(self.screen, cell_background, rectangle)

                if symbol:
                    text = self.font.render(symbol, True, symbol_color)
                    self.screen.blit(text, text.get_rect(center=rectangle.center))

                if self.show_grid_lines:
                    pygame.draw.rect(self.screen, GRID_COLOR, rectangle, 1)

        pygame.display.flip()

    def run(self):
        running = True
        self.draw_grid()

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_g:
                    self.show_grid_lines = not self.show_grid_lines
                    self.draw_grid()

        pygame.quit()
