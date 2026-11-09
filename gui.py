import pygame
from grid import STATIC_WALLS, TREASURE, TRAP, START
from algos.dfs import DFS
from algos.bfs import BFS 

CELL_SIZE = 40
SIDEBAR_WIDTH = 220
BUTTON_WIDTH = 180
BUTTON_HEIGHT = 32
BACKGROUND_COLOR = (255, 255, 255)
BUTTON_AREA_BACKGROUND = (49, 18, 171)
GRID_COLOR = (0, 0, 0)
WALL_BACKGROUND = (79, 129, 224)
TREASURE_BACKGROUND = (255, 193, 29)
TRAP_BACKGROUND = (255, 0, 0)
START_BACKGROUND = (34, 177, 76)
BUTTON_BACKGROUND = (79, 129, 224)
BUTTON_TEXT_COLOR = (255, 255, 255)
WALL_TEXT_COLOR = (0, 0, 0)
TREASURE_TEXT_COLOR = (255, 255, 255)
TRAP_TEXT_COLOR = (255, 255, 255)
START_TEXT_COLOR = (255, 255, 255)
VISITED_BACKGROUND = (94, 237, 136)
SOLUTION_PATH_BACKGROUND = (94, 237, 136)
SOLUTION_PATH_SYMBOL_COLOR = (255,255,255)
WEIGHT_TEXT_COLOR = (0, 0, 0)
DROPDOWN_SELECTED_BACKGROUND = (45, 85, 165)
DROPDOWN_BORDER_COLOR = (255, 255, 255)
DISABLED_BUTTON_BACKGROUND = (70, 85, 130)
DISABLED_TEXT_COLOR = (150, 160, 190)
ALGORITHMS = ["DFS", "BFS", "UCS", "A*"]

class Gui:

    def __init__(
        self, grid, on_regenerate, on_run=None, show_grid_lines=True,
        on_algo_change=None, custom_grid_names=None, on_custom_grid=None,
    ):
        if not grid:
            raise ValueError("2d matrix of size 8x8 or more should be inserted", grid)

        pygame.init()
        self.grid = grid
        self.on_regenerate = on_regenerate
        self.on_run = on_run
        self.on_algo_change = on_algo_change
        self.custom_grid_names = list(custom_grid_names or [])
        self.on_custom_grid = on_custom_grid
        self.show_grid_lines = show_grid_lines
        self.font = pygame.font.Font(None, 32)
        self.weight_font = pygame.font.Font(None, 18)
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
        self.custom_grid_button = pygame.Rect(0, 0, BUTTON_WIDTH, BUTTON_HEIGHT)
        self._layout_buttons()
        pygame.display.set_caption("Treasure Hunt")

        self.current_algo_idx = 0
        self.dropdown_open = False
        self.custom_grid_dropdown_open = False
        self.current_custom_grid_idx = None
        self.solution_path = []
        self.visited = []
        self.weights = None
        self.info = None
        self.animate_pending = False
        self.skip_animation = False
        # True only while the search animation plays; the sidebar is locked then
        self.busy = False

    def _layout_buttons(self):
        button_x = self.screen.get_width() - BUTTON_WIDTH - 20
        start_y = 20
        button_spacing = 12

        self.custom_grid_button.topleft = (button_x, start_y)
        self.regenerate_button.topleft = (button_x, start_y + BUTTON_HEIGHT + button_spacing)
        self.reset_overlay_button.topleft = (button_x, start_y + 2 * (BUTTON_HEIGHT + button_spacing))
        self.run_button.topleft = (button_x, start_y + 3 * (BUTTON_HEIGHT + button_spacing))
        self.selected_algo_button.topleft = (button_x, start_y + 4 * (BUTTON_HEIGHT + button_spacing))

    def set_weights(self, weights):
        self.weights = weights

    def set_solution_path(self, solution):
        self.solution_path = list(solution or [])
        self.animate_pending = bool(self.solution_path)

    def set_visited(self, visited):
        self.visited = list(visited or [])
        self.animate_pending = bool(self.visited)

    def get_screen_size(self):
        return (
            SIDEBAR_WIDTH + CELL_SIZE * len(self.grid[0]),
            CELL_SIZE * len(self.grid),
        )

    def _button_background(self):
        return DISABLED_BUTTON_BACKGROUND if self.busy else BUTTON_BACKGROUND

    def _button_text_color(self):
        return DISABLED_TEXT_COLOR if self.busy else BUTTON_TEXT_COLOR

    def _sidebar_rect(self):
        return pygame.Rect(
            self.screen.get_width() - SIDEBAR_WIDTH, 0, SIDEBAR_WIDTH, self.screen.get_height()
        )

    def _dropdown_option_rects(self):
        # the list opens below the header, or above it when there is no room
        list_height = len(ALGORITHMS) * BUTTON_HEIGHT
        top = self.selected_algo_button.bottom
        if self.custom_grid_names or top + list_height > self.screen.get_height():
            top = self.selected_algo_button.top - list_height

        return [
            pygame.Rect(self.selected_algo_button.x, top + i * BUTTON_HEIGHT, BUTTON_WIDTH, BUTTON_HEIGHT)
            for i in range(len(ALGORITHMS))
        ]

    def _select_algorithm(self, idx):
        if idx == self.current_algo_idx:
            return

        self.current_algo_idx = idx
        self._clear_results()  # overlay AND the stats text belong to the old algorithm
        if self.on_algo_change:
            self.on_algo_change()

    def _custom_grid_option_rects(self):
        return [
            pygame.Rect(
                self.custom_grid_button.x,
                self.custom_grid_button.bottom + i * BUTTON_HEIGHT,
                BUTTON_WIDTH,
                BUTTON_HEIGHT,
            )
            for i in range(len(self.custom_grid_names))
        ]

    def _select_custom_grid(self, idx):
        self.current_custom_grid_idx = idx
        self.grid = self.on_custom_grid(idx)
        self.screen = pygame.display.set_mode(self.get_screen_size())
        self._layout_buttons()
        self._clear_results()

    def _handle_custom_grid_dropdown_click(self, pos):
        if not self.custom_grid_names:
            return False

        if self.custom_grid_button.collidepoint(pos):
            self.dropdown_open = False
            self.custom_grid_dropdown_open = not self.custom_grid_dropdown_open
            return True

        if not self.custom_grid_dropdown_open:
            return False

        self.custom_grid_dropdown_open = False
        for idx, rect in enumerate(self._custom_grid_option_rects()):
            if rect.collidepoint(pos):
                self._select_custom_grid(idx)
                break
        return True

    def _handle_dropdown_click(self, pos):
        # returns True when the click was used up by the dropdown
        if self.selected_algo_button.collidepoint(pos):
            self.custom_grid_dropdown_open = False
            self.dropdown_open = not self.dropdown_open
            return True

        if not self.dropdown_open:
            return False

        # an open list takes the click first, even when it lands on nothing,
        # so closing it can never trigger the button underneath
        self.dropdown_open = False
        for idx, rect in enumerate(self._dropdown_option_rects()):
            if rect.collidepoint(pos):
                self._select_algorithm(idx)
                break
        return True

    def _draw_dropdown(self):
        header = self.selected_algo_button
        header_text = self.button_font.render(
            f"Algorithm: {ALGORITHMS[self.current_algo_idx]}", True, self._button_text_color()
        )
        self.screen.blit(header_text, header_text.get_rect(midleft=(header.x + 10, header.centery)))

        # triangle on the right: down when closed, up when open
        arrow_x, arrow_y = header.right - 18, header.centery
        if self.dropdown_open:
            points = [(arrow_x - 6, arrow_y + 3), (arrow_x + 6, arrow_y + 3), (arrow_x, arrow_y - 4)]
        else:
            points = [(arrow_x - 6, arrow_y - 3), (arrow_x + 6, arrow_y - 3), (arrow_x, arrow_y + 4)]
        pygame.draw.polygon(self.screen, self._button_text_color(), points)

        if not self.dropdown_open:
            return

        for idx, rect in enumerate(self._dropdown_option_rects()):
            background = DROPDOWN_SELECTED_BACKGROUND if idx == self.current_algo_idx else BUTTON_BACKGROUND
            pygame.draw.rect(self.screen, background, rect)
            pygame.draw.rect(self.screen, DROPDOWN_BORDER_COLOR, rect, 1)
            option_text = self.button_font.render(ALGORITHMS[idx], True, BUTTON_TEXT_COLOR)
            self.screen.blit(option_text, option_text.get_rect(midleft=(rect.x + 10, rect.centery)))

    def _draw_custom_grid_dropdown(self):
        if not self.custom_grid_names:
            return

        header = self.custom_grid_button
        label = "Custom Grid"
        if self.current_custom_grid_idx is not None:
            label = self.custom_grid_names[self.current_custom_grid_idx]
        header_text = self.button_font.render(label, True, self._button_text_color())
        self.screen.blit(header_text, header_text.get_rect(midleft=(header.x + 10, header.centery)))

        arrow_x, arrow_y = header.right - 18, header.centery
        if self.custom_grid_dropdown_open:
            points = [(arrow_x - 6, arrow_y + 3), (arrow_x + 6, arrow_y + 3), (arrow_x, arrow_y - 4)]
        else:
            points = [(arrow_x - 6, arrow_y - 3), (arrow_x + 6, arrow_y - 3), (arrow_x, arrow_y + 4)]
        pygame.draw.polygon(self.screen, self._button_text_color(), points)

        if not self.custom_grid_dropdown_open:
            return

        for idx, rect in enumerate(self._custom_grid_option_rects()):
            selected = idx == self.current_custom_grid_idx
            pygame.draw.rect(self.screen, DROPDOWN_SELECTED_BACKGROUND if selected else BUTTON_BACKGROUND, rect)
            pygame.draw.rect(self.screen, DROPDOWN_BORDER_COLOR, rect, 1)
            option_text = self.button_font.render(self.custom_grid_names[idx], True, BUTTON_TEXT_COLOR)
            self.screen.blit(option_text, option_text.get_rect(midleft=(rect.x + 10, rect.centery)))

    def _cell_rect(self, r, c):
        return pygame.Rect(
            self.board_origin_x + c * CELL_SIZE,
            r * CELL_SIZE,
            CELL_SIZE,
            CELL_SIZE,
        )

    def _animation_interrupted(self):
        for event in pygame.event.get([pygame.QUIT, pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN]):
            if event.type == pygame.QUIT:
                pygame.event.post(event)
            elif event.type == pygame.MOUSEBUTTONDOWN and self._sidebar_rect().collidepoint(event.pos):
                # a locked button: swallow the click, keep animating
                continue
            return True
        pygame.event.pump()
        return False

    def _animate_cells(self, cells, background, with_symbol,waittime = 50):
        for r, c in cells:
            if not (0 <= r < len(self.grid) and 0 <= c < len(self.grid[0])):
                continue
            if self.grid[r][c] in (START, TREASURE):
                continue

            rect = self._cell_rect(r, c)
            pygame.draw.rect(self.screen, background, rect)

            if with_symbol:
                pygame.draw.circle(self.screen, SOLUTION_PATH_SYMBOL_COLOR, rect.center, CELL_SIZE // 6)
            if self.show_grid_lines:
                pygame.draw.rect(self.screen, GRID_COLOR, rect, 1)

            if not self.skip_animation:
                pygame.display.update(rect)
                if self._animation_interrupted():
                    self.skip_animation = True
                else:
                    pygame.time.wait(waittime)

    def _draw_visited(self):
        self.skip_animation = not self.animate_pending
        self.animate_pending = False
        self._animate_cells(self.visited, VISITED_BACKGROUND, False)
        self._animate_cells(self.solution_path, SOLUTION_PATH_BACKGROUND, True)


    def show_info(self, total_cost, nodes_expanded, execution_time):
        self.info = (total_cost, nodes_expanded, execution_time)

    def _draw_info(self):
        if not self.info or self.busy:
            return

        total_cost, nodes_expanded, execution_time = self.info
        lines = [
            f"Path cost: {total_cost}",
            f"Nodes expanded: {nodes_expanded}",
            f"Time: {execution_time:.4f}s",
        ]

        x = self.selected_algo_button.x
        y = self.selected_algo_button.bottom + 20
        for line in lines:
            surface = self.button_font.render(line, True, BUTTON_TEXT_COLOR)
            self.screen.blit(surface, (x, y))
            y += surface.get_height() + 6


    def _draw_weights(self):
        if not self.weights:
            return

        for r, row in enumerate(self.weights):
            for c, weight in enumerate(row):
                if weight is None:
                    continue

                text = self.weight_font.render(str(weight), True, WEIGHT_TEXT_COLOR)
                x = self.board_origin_x + c * CELL_SIZE + CELL_SIZE // 2
                y = (r + 1) * CELL_SIZE - 2
                self.screen.blit(text, text.get_rect(midbottom=(x, y)))

    def _draw_board(self):
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
                elif cell == TREASURE:
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

    def _draw_sidebar(self):
        # Everything in the sidebar, in one place, so it is always painted
        # completely. While self.busy it is drawn dimmed (locked) and the
        # results are hidden until the animation is over.
        pygame.draw.rect(self.screen, BUTTON_AREA_BACKGROUND, self._sidebar_rect())

        background = self._button_background()
        pygame.draw.rect(self.screen, background, self.regenerate_button)
        pygame.draw.rect(self.screen, background, self.run_button)
        pygame.draw.rect(self.screen, background, self.reset_overlay_button)
        pygame.draw.rect(self.screen, background, self.selected_algo_button)
        if self.custom_grid_names:
            pygame.draw.rect(self.screen, background, self.custom_grid_button)

        text_color = self._button_text_color()
        for label, button in (
            ("Regenerate Grid", self.regenerate_button),
            ("Run", self.run_button),
            ("Reset View", self.reset_overlay_button),
        ):
            text = self.button_font.render(label, True, text_color)
            self.screen.blit(text, text.get_rect(center=button.center))

        self._draw_info()
        self._draw_dropdown()
        self._draw_custom_grid_dropdown()

    def draw_grid(self):
        self._draw_board()
        self._draw_sidebar()
        self._draw_visited()
        self._draw_weights()
        pygame.display.flip()

    def regenerate_grid(self):
        self.grid = self.on_regenerate()
        self.current_custom_grid_idx = None
        self.screen = pygame.display.set_mode(self.get_screen_size())
        self.board_origin_x = 0
        self._layout_buttons()
        self._clear_results()
        self.draw_grid()

    def reset_overlay(self):
        self._clear_results()
        self.draw_grid()

    def _set_busy(self, busy):
        self.busy = busy
        if busy:
            # a "hand" cursor left over Run would suggest it is still clickable
            pygame.mouse.set_cursor(self.arrow_cursor)
            self.button_hovered = False

    def run_algorithm(self):
        if not self.on_run:
            return

        # lock first, so the sidebar dims on the very frame after the click
        self._set_busy(True)
        try:
            self._clear_results()
            self.draw_grid()   # instant: dimmed sidebar, old results gone
            self.on_run()      # compute the search (fast)
            self.draw_grid()   # animate the overlay
        finally:
            self._set_busy(False)
        self.draw_grid()       # unlock: normal colours, results appear

    def _clear_results(self):
        self.visited = []
        self.solution_path = []
        self.info = None
        self.animate_pending = False

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
                elif (
                    event.type == pygame.KEYDOWN
                    and event.key == pygame.K_ESCAPE
                    and (self.dropdown_open or self.custom_grid_dropdown_open)
                ):
                    self.dropdown_open = False
                    self.custom_grid_dropdown_open = False
                    self.draw_grid()
                elif (
                    event.type == pygame.MOUSEBUTTONDOWN
                    and event.button == 1
                    and (
                        self._handle_custom_grid_dropdown_click(event.pos)
                        or self._handle_dropdown_click(event.pos)
                    )
                ):
                    self.draw_grid()
                elif event.type == pygame.MOUSEMOTION:
                    hovering = (
                        self.regenerate_button.collidepoint(event.pos)
                        or self.run_button.collidepoint(event.pos)
                        or self.reset_overlay_button.collidepoint(event.pos)
                        or self.selected_algo_button.collidepoint(event.pos)
                        or (self.custom_grid_names and self.custom_grid_button.collidepoint(event.pos))
                        or (self.dropdown_open and any(
                            rect.collidepoint(event.pos) for rect in self._dropdown_option_rects()
                        ))
                        or (self.custom_grid_dropdown_open and any(
                            rect.collidepoint(event.pos) for rect in self._custom_grid_option_rects()
                        ))
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

        pygame.quit()
