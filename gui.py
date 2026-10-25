import pygame
from grid import STATIC_WALLS, TRESURE, TRAP, START
from algos.dfs import DFS
from algos.bfs import BFS 

CELL_SIZE = 40
SIDEBAR_WIDTH = 220
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
VISITED_BACKGROUND = (200, 230, 255)
SOLUTION_PATH_BACKGROUND = (160, 240, 160)
ALGORITHMS = ["DFS", "BFS"]

class Gui:

    def __init__(self, grid, on_regenerate, on_run=None, show_grid_lines=True):
        if not grid:
            raise ValueError("2d matrix of size 8x8 or more should be inserted", grid)

        pygame.init()
        self.grid = grid
        self.on_regenerate = on_regenerate
        self.on_run = on_run
        self.show_grid_lines = show_grid_lines
        self.font = pygame.font.Font(None, 32)
        self.button_font = pygame.font.Font(None, 24)
        self.arrow_cursor = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_ARROW)
        self.hand_cursor = pygame.cursors.Cursor(pygame.SYSTEM_CURSOR_HAND)
        self.button_hovered = False
        self.screen = pygame.display.set_mode(self.get_screen_size())
        self.board_origin_x = 0
        self.regenerate_button = pygame.Rect(0, 0, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.run_button = pygame.Rect(0, 0, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.reset_overlay_button = pygame.Rect(0, 0, BUTTON_WIDTH, BUTTON_HEIGHT)
        self.selected_algo_button = pygame.Rect(0, 0, BUTTON_WIDTH, BUTTON_HEIGHT)

        button_x = self.screen.get_width() - BUTTON_WIDTH - 20
        start_y = 20
        button_spacing = 12

        self.regenerate_button.topleft = (button_x, start_y)
        self.reset_overlay_button.topleft = (button_x, start_y + BUTTON_HEIGHT + button_spacing) 
        self.run_button.topleft = (button_x, start_y + 2 * (BUTTON_HEIGHT + button_spacing))
        self.selected_algo_button.topleft = (button_x, start_y + 3 * (BUTTON_HEIGHT + button_spacing))
        pygame.display.set_caption("Treasure Hunt")

        self.current_algo_idx = 0
        self.solution_path = []
        self.visited = []

    def set_solution_path(self, solution):
        self.solution_path = list(solution or [])

    def set_visited(self, visited):
        self.visited = list(visited or [])

    def get_screen_size(self):
        return (
            SIDEBAR_WIDTH + CELL_SIZE * len(self.grid[0]),
            CELL_SIZE * len(self.grid),
        )

    def _update_algorithm(self):
        self.current_algo_idx += 1
        if (self.current_algo_idx == len(ALGORITHMS)):
            self.current_algo_idx = 0

    def _draw_visited(self):
        path_set = set(self.solution_path)

        for r, c in self.visited:
            if r < 0 or c < 0:
                continue
            if r >= len(self.grid) or c >= len(self.grid[0]):
                continue

            cell = self.grid[r][c]
            if cell in (START, TRESURE):
                continue

            rectangle = pygame.Rect(
                self.board_origin_x + c * CELL_SIZE,
                r * CELL_SIZE,
                CELL_SIZE,
                CELL_SIZE,
            )

            if (r, c) in path_set:
                pygame.draw.rect(self.screen, SOLUTION_PATH_BACKGROUND, rectangle)
                pygame.draw.circle(self.screen, (0, 120, 0), rectangle.center, CELL_SIZE // 6)
            else:
                pygame.draw.rect(self.screen, VISITED_BACKGROUND, rectangle)

            if self.show_grid_lines:
                pygame.draw.rect(self.screen, GRID_COLOR, rectangle, 1)

    def draw_grid(self):
        self.screen.fill(BACKGROUND_COLOR)

        for row in range(len(self.grid)):
            for col in range(len(self.grid[row])):
                rectangle = pygame.Rect(
                    self.board_origin_x + col * CELL_SIZE,
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

        sidebar_area = pygame.Rect(
            self.screen.get_width() - SIDEBAR_WIDTH,
            0,
            SIDEBAR_WIDTH,
            self.screen.get_height(),
        )

        #DRAWING ALL THE BUTTONS
        pygame.draw.rect(self.screen, BUTTON_AREA_BACKGROUND, sidebar_area)
        pygame.draw.rect(self.screen, BUTTON_BACKGROUND, self.regenerate_button)
        pygame.draw.rect(self.screen, BUTTON_BACKGROUND, self.run_button)
        pygame.draw.rect(self.screen, BUTTON_BACKGROUND, self.reset_overlay_button)
        pygame.draw.rect(self.screen, BUTTON_BACKGROUND, self.selected_algo_button)

        #DRAWING ALL THE TEXT FOR THE BUTTONS
        regenerate_text = self.button_font.render("Regenerate Grid", True, BUTTON_TEXT_COLOR)
        self.screen.blit(
            regenerate_text,
            regenerate_text.get_rect(center=self.regenerate_button.center),
        )

        run_text = self.button_font.render("Run", True, BUTTON_TEXT_COLOR)
        self.screen.blit(
            run_text,
            run_text.get_rect(center=self.run_button.center),
        )

        reset_text = self.button_font.render("Reset View", True, BUTTON_TEXT_COLOR)
        self.screen.blit(
            reset_text,
            reset_text.get_rect(center=self.reset_overlay_button.center),
        )

        algo_text = self.button_font.render(ALGORITHMS[self.current_algo_idx], True, BUTTON_TEXT_COLOR)
        self.screen.blit(
            algo_text,
            algo_text.get_rect(center=self.selected_algo_button.center),
        )

        self._draw_visited()
        pygame.display.flip()

    def regenerate_grid(self):
        self.grid = self.on_regenerate()
        self.screen = pygame.display.set_mode(self.get_screen_size())
        self.board_origin_x = 0
        button_x = self.screen.get_width() - BUTTON_WIDTH - 20
        start_y = 20
        button_spacing = 12

        self.regenerate_button.topleft = (button_x, start_y)
        self.run_button.topleft = (button_x, start_y + BUTTON_HEIGHT + button_spacing)
        self.reset_overlay_button.topleft = (button_x, start_y + 2 * (BUTTON_HEIGHT + button_spacing))
        self.selected_algo_button.topleft = (button_x, start_y + 3 * (BUTTON_HEIGHT + button_spacing))
        self.visited = []
        self.solution_path = []
        self.draw_grid()

    def reset_overlay(self):
        self.visited = []
        self.solution_path = []
        self.draw_grid()

    def run_algorithm(self):
        if self.on_run:
            self.on_run()
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
                    hovering = (
                        self.regenerate_button.collidepoint(event.pos)
                        or self.run_button.collidepoint(event.pos)
                        or self.reset_overlay_button.collidepoint(event.pos)
                    )
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
                elif (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                    and self.run_button.collidepoint(event.pos)
                ):
                    self.run_algorithm()
                elif (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                    and self.reset_overlay_button.collidepoint(event.pos)
                ):
                    self.reset_overlay()
                elif (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                    and self.selected_algo_button.collidepoint(event.pos)
                ):
                    self._update_algorithm()
                    self.draw_grid()

        pygame.quit()
