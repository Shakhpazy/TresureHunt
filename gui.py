import pygame
from grid import STATIC_WALLS, TRESURE, TRAP, START

CELL_SIZE = 40
BUTTON_AREA_HEIGHT = 44
BUTTON_WIDTH = 180
BUTTON_HEIGHT = 32
BACKGROUND_COLOR = (255, 255, 255)
BUTTON_AREA_BACKGROUND = (0, 0, 0)
GRID_COLOR = (0, 0, 0)
WALL_BACKGROUND = (255, 220, 0)
TREASURE_BACKGROUND = (255, 170, 200)
TRAP_BACKGROUND = (0, 220, 220)
START_BACKGROUND = (170, 220, 170)
BUTTON_BACKGROUND = (55, 105, 170)
BUTTON_TEXT_COLOR = (255, 255, 255)
WALL_TEXT_COLOR = (0, 0, 0)
TREASURE_TEXT_COLOR = (0, 140, 0)
TRAP_TEXT_COLOR = (220, 0, 0)
START_TEXT_COLOR = (0, 0, 0)

class Gui:

    def __init__(self, grid, on_regenerate, show_grid_lines=True):
        if not grid:
            raise ValueError("2d matrix of size 8x8 or more should be inserted", grid)

        pygame.init()
        self.grid = grid
        self.on_regenerate = on_regenerate
        self.show_grid_lines = show_grid_lines
        self.font = pygame.font.Font(None, 32)
        self.button_font = pygame.font.Font(None, 24)
        self.arrow_cursor = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_ARROW)
        self.hand_cursor = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_HAND)
        self.button_hovered = False
        self.screen = pygame.display.set_mode(self.get_screen_size())
        self.regenerate_button = pygame.Rect(0, 0, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.regenerate_button.centerx = self.screen.get_width() // 2
        self.regenerate_button.centery = len(self.grid) * CELL_SIZE + BUTTON_AREA_HEIGHT // 2
        pygame.display.set_caption("Treasure Hunt")

    def get_screen_size(self):
        return (
            CELL_SIZE * len(self.grid[0]),
            CELL_SIZE * len(self.grid) + BUTTON_AREA_HEIGHT,
        )

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
                elif cell == START:
                    cell_background = START_BACKGROUND
                    symbol = "S"
                    symbol_color = START_TEXT_COLOR

                pygame.draw.rect(self.screen, cell_background, rectangle)

                if symbol:
                    text = self.font.render(symbol, True, symbol_color)
                    self.screen.blit(text, text.get_rect(center=rectangle.center))

                if self.show_grid_lines:
                    pygame.draw.rect(self.screen, GRID_COLOR, rectangle, 1)

        button_area = pygame.Rect(
            0,
            len(self.grid) * CELL_SIZE,
            self.screen.get_width(),
            BUTTON_AREA_HEIGHT,
        )
        pygame.draw.rect(self.screen, BUTTON_AREA_BACKGROUND, button_area)
        pygame.draw.rect(self.screen, BUTTON_BACKGROUND, self.regenerate_button)
        button_text = self.button_font.render("Regenerate Grid", True, BUTTON_TEXT_COLOR)
        self.screen.blit(
            button_text,
            button_text.get_rect(center=self.regenerate_button.center),
        )
        pygame.display.flip()

    def regenerate_grid(self):
        self.grid = self.on_regenerate()
        self.screen = pygame.display.set_mode(self.get_screen_size())
        self.regenerate_button.centerx = self.screen.get_width() // 2
        self.regenerate_button.centery = len(self.grid) * CELL_SIZE + BUTTON_AREA_HEIGHT // 2
        self.draw_grid()

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
                elif event.type == pygame.MOUSEMOTION:
                    hovering = self.regenerate_button.collidepoint(event.pos)
                    if hovering != self.button_hovered:
                        self.button_hovered = hovering
                        cursor = self.hand_cursor if hovering else self.arrow_cursor
                        pygame.mouse.set_cursor(cursor)
                elif (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                    and self.regenerate_button.collidepoint(event.pos)
                ):
                    self.regenerate_grid()

        pygame.quit()
