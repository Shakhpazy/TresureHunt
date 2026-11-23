"""The two-player game in Pygame. Open from main.py or python -m adversarial.gui."""
import time

import pygame

from adversarial.players import SearchPlayer
from adversarial.session import ALGORITHMS, DEPTHS, EVAL_NAMES, MODES, GameSession
from gui import (BACKGROUND_COLOR, BUTTON_AREA_BACKGROUND, BUTTON_BACKGROUND,
                 BUTTON_TEXT_COLOR, DISABLED_BUTTON_BACKGROUND, DISABLED_TEXT_COLOR,
                 GRID_COLOR, TREASURE_BACKGROUND, TRAP_BACKGROUND, WALL_BACKGROUND)

CELL_SIZE = 36
BOARD_X, BOARD_Y = 20, 86
SCREEN_SIZE = (1000, 780)
AGENT_COLORS = ((5, 150, 105), (124, 58, 237))
MOVE_DELAY = 35  # match the earlier search animation
SKIP_FRAME_BUDGET = 0.012  # keep processing clicks and close events while skipping


class AdversarialGui:
    def __init__(self, seed=None, out=print):
        pygame.init()
        self.screen = pygame.display.set_mode(SCREEN_SIZE)
        pygame.display.set_caption("Treasure Hunt - Two-player game")
        self.font = pygame.font.Font(None, 25)
        self.small_font = pygame.font.Font(None, 21)
        self.title_font = pygame.font.Font(None, 34)
        self.session = GameSession(seed, out)
        self.running = False
        self.skip_animation = False
        self.next_move_at = 0
        self.show_grid_lines = True
        self.buttons = {
            "back": pygame.Rect(600, 20, 380, 36),
            "mode": pygame.Rect(600, 70, 380, 36),
            "algo_a": pygame.Rect(600, 120, 184, 36),
            "algo_b": pygame.Rect(796, 120, 184, 36),
            "depth_a": pygame.Rect(600, 166, 184, 36),
            "depth_b": pygame.Rect(796, 166, 184, 36),
            "eval_a": pygame.Rect(600, 212, 184, 36),
            "eval_b": pygame.Rect(796, 212, 184, 36),
            "compare": pygame.Rect(600, 258, 380, 36),
            "run": pygame.Rect(600, 308, 184, 40),
            "step": pygame.Rect(796, 308, 184, 40),
            "reset": pygame.Rect(600, 360, 184, 36),
            "new": pygame.Rect(796, 360, 184, 36),
        }

    def _text(self, text, x, y, color=(30, 41, 59), small=False, title=False):
        font = self.title_font if title else self.small_font if small else self.font
        self.screen.blit(font.render(text, True, color), (x, y))

    def _cell_rect(self, cell):
        r, c = cell
        return pygame.Rect(BOARD_X + c * CELL_SIZE, BOARD_Y + r * CELL_SIZE, CELL_SIZE, CELL_SIZE)

    def _labels(self):
        game = self.session
        labels = {
            "back": "Back to search algorithms",
            "mode": f"Mode: {game.mode}  >",
            "compare": f"Compare both searches: {'On' if game.compare else 'Off'}  >",
            "run": "Pause" if self.running else "Run game",
            "step": ("Skipping..." if self.skip_animation else "Skip animation") if self.running else "Step one turn",
            "reset": "Reset same map",
            "new": "New map",
        }
        for who, suffix in enumerate(("a", "b")):
            labels[f"algo_{suffix}"] = f"{'AB'[who]}: {game.algorithms[who].name}  >"
            labels[f"depth_{suffix}"] = f"Depth: {game.depths[who]}  >"
            labels[f"eval_{suffix}"] = f"Evaluation: {game.evaluations[who].split()[0]}  >"
        if game.mode != "AI vs AI":
            labels["algo_b"] = "B: Human" if game.mode == "Human vs AI" else "B: Random"
            labels["depth_b"] = "Depth: --"
            labels["eval_b"] = "Evaluation: --"
        return labels

    def _enabled(self, name):
        if name.endswith("_b") and self.session.mode != "AI vs AI":
            return False
        if name in ("run", "step") and self.session.state.is_terminal():
            return False
        if name == "step" and self.running and self.skip_animation:
            return False
        if self.running and name not in ("back", "run", "step", "reset", "new"):
            return False
        return True

    def _draw_board(self):
        game, state = self.session, self.session.state
        self._text("Treasure Hunt", 20, 16, title=True)
        self._text(f"15 x 15  |  Map seed {game.seed}", 304, 24, small=True)
        self._text(game.status(), 20, 56, small=True)
        for r, row in enumerate(state.grid):
            for c, cell in enumerate(row):
                position = (r, c)
                rect = self._cell_rect(position)
                color, glyph = BACKGROUND_COLOR, ""
                if cell == "#":
                    color, glyph = WALL_BACKGROUND, "#"
                elif position in state.traps:
                    color, glyph = TRAP_BACKGROUND, "X"
                elif position in state.treasures:
                    color, glyph = TREASURE_BACKGROUND, "T"
                pygame.draw.rect(self.screen, color, rect)
                if glyph:
                    text = self.font.render(glyph, True, (255, 255, 255) if glyph != "T" else (69, 26, 3))
                    self.screen.blit(text, text.get_rect(center=rect.center))
                if self.show_grid_lines:
                    pygame.draw.rect(self.screen, GRID_COLOR, rect, 1)
        for who, path in enumerate(game.paths):
            if len(path) > 1:
                # Offset the trails slightly so shared cells show both players.
                points = [(self._cell_rect(cell).centerx + (who * 6 - 3),
                           self._cell_rect(cell).centery + (who * 6 - 3)) for cell in path]
                pygame.draw.lines(self.screen, AGENT_COLORS[who], False, points, 3)
        if game.is_human_turn():
            for move in state.legal_moves():
                if move is not None:
                    pygame.draw.rect(self.screen, AGENT_COLORS[1], self._cell_rect(move).inflate(-6, -6), 3)
        for who, cell in enumerate(state.pos):
            rect = self._cell_rect(cell)
            pygame.draw.circle(self.screen, AGENT_COLORS[who], rect.center, 15)
            pygame.draw.circle(self.screen, (255, 255, 255), rect.center, 15, 2)
            text = self.font.render("AB"[who], True, (255, 255, 255))
            self.screen.blit(text, text.get_rect(center=rect.center))
        self._text("A: green   B: purple   T: treasure   X / #: blocked", 20, 640, small=True)
        self._text("Space: run/pause   N: step   G: grid lines   Esc: back", 20, 664, small=True)
        self._text("E1: lead + distance   E2: + trap proximity   E3: + race", 20, 688, small=True)
        hint = "Click board or press Enter to skip animation." if self.running else (
            "Changing settings restarts this map. Click > to cycle.")
        self._text(hint, 20, 712, small=True)
        if game.log:
            # Search metrics are shown in the sidebar; the footer shows the action.
            self._text(game.last_action, 20, 746, small=True)

    def _draw_stats(self):
        game, state = self.session, self.session.state
        white = BUTTON_TEXT_COLOR
        self._text("Treasures collected", 600, 416, white)
        self._text(f"A: {state.scores[0]}     B: {state.scores[1]}     Left: {len(state.treasures)}", 600, 444, white)
        self._text(f"Turn {state.plies}/{state.max_plies}   Moves A: {game.moves[0]}  B: {game.moves[1]}",
                   600, 472, white, small=True)
        for who, player in enumerate(game.players):
            y = 508 + who * 58
            if isinstance(player, SearchPlayer):
                self._text(f"{'AB'[who]} {player.label}", 600, y, white, small=True)
                self._text(f"{player.nodes_expanded:,} nodes | {player.elapsed:.4f}s | {player.cutoffs:,} cutoffs",
                           600, y + 23, white, small=True)
            else:
                self._text(f"{'AB'[who]}: {'Human' if player is None else 'Random'} - no search", 600, y, white, small=True)
        self._text("Search comparison (totals)", 600, 640, white)
        ratio = game.pruning_ratio()
        if ratio is None:
            self._text("Turn comparison on, then run or step.", 600, 671, white, small=True)
            self._text("Uses the same positions and evaluation.", 600, 697, white, small=True)
        else:
            for index, name in enumerate(("Minimax", "Alpha-Beta")):
                stats = game.comparison[name]
                self._text(f"{name}: {stats['nodes']:,} nodes / {stats['time']:.4f}s",
                           600, 670 + index * 25, white, small=True)
            self._text(f"Pruned: {ratio:.1%} | moves and values agree", 600, 726, white, small=True)
        self._text("Time measures search, excluding animation.", 600, 754, white, small=True)

    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)
        pygame.draw.rect(self.screen, BUTTON_AREA_BACKGROUND, (580, 0, 420, SCREEN_SIZE[1]))
        self._draw_board()
        for name, label in self._labels().items():
            enabled = self._enabled(name)
            rect = self.buttons[name]
            pygame.draw.rect(self.screen, BUTTON_BACKGROUND if enabled else DISABLED_BUTTON_BACKGROUND, rect, border_radius=5)
            text = self.font.render(label, True, BUTTON_TEXT_COLOR if enabled else DISABLED_TEXT_COLOR)
            self.screen.blit(text, text.get_rect(center=rect.center))
        self._draw_stats()
        pygame.display.flip()

    def action(self, name):
        if not self._enabled(name):
            return
        game = self.session
        if name == "run":
            self.running = not self.running
            self.skip_animation = False
            self.next_move_at = pygame.time.get_ticks()
            return
        if name == "step":
            if self.running:
                self.skip_animation = True
                self.next_move_at = 0
            else:
                game.step()
            return
        if name in ("reset", "new"):
            self.running = False
            self.skip_animation = False
            game.reset(regenerate=name == "new")
            return
        if name == "mode":
            game.mode = MODES[(MODES.index(game.mode) + 1) % len(MODES)]
        elif name == "compare":
            game.compare = not game.compare
        elif name.startswith(("algo_", "depth_", "eval_")):
            who = 0 if name.endswith("_a") else 1
            values, options = (game.algorithms, ALGORITHMS) if name.startswith("algo") else (
                (game.depths, DEPTHS) if name.startswith("depth") else (game.evaluations, EVAL_NAMES))
            values[who] = options[(options.index(values[who]) + 1) % len(options)]
        else:
            return
        self.skip_animation = False
        game.reset()

    def handle_event(self, event):
        # Return "back" or "quit" to the parent window; no nested pygame.quit().
        if event.type == pygame.QUIT:
            return "quit"
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return "back"
            if event.key == pygame.K_SPACE:
                self.action("run")
            elif event.key == pygame.K_n:
                self.action("step")
            elif event.key == pygame.K_g:
                self.show_grid_lines = not self.show_grid_lines
            elif event.key == pygame.K_RETURN:
                if self.running:
                    self.action("step")
            elif self.session.is_human_turn():
                directions = {pygame.K_UP: (-1, 0), pygame.K_DOWN: (1, 0),
                              pygame.K_LEFT: (0, -1), pygame.K_RIGHT: (0, 1)}
                if event.key in directions:
                    r, c = self.session.state.pos[1]
                    dr, dc = directions[event.key]
                    if self.session.step((r + dr, c + dc)):
                        self.next_move_at = pygame.time.get_ticks() + MOVE_DELAY
            elif self.running:
                # Like the earlier view, ordinary keys skip the animation.
                # The existing pause, grid, back and human-move keys keep their jobs.
                self.action("step")
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for name, rect in self.buttons.items():
                if rect.collidepoint(event.pos):
                    if name == "back":
                        return "back"
                    self.action(name)
                    return
            board = pygame.Rect(BOARD_X, BOARD_Y, CELL_SIZE * 15, CELL_SIZE * 15)
            if board.collidepoint(event.pos) and self.session.is_human_turn():
                x, y = event.pos
                if self.session.step(((y - BOARD_Y) // CELL_SIZE, (x - BOARD_X) // CELL_SIZE)):
                    self.next_move_at = pygame.time.get_ticks() + MOVE_DELAY
            elif board.collidepoint(event.pos) and self.running:
                self.action("step")

    def update(self, now):
        if self.session.state.is_terminal():
            self.running = False
        deadline = time.perf_counter() + SKIP_FRAME_BUDGET
        while self.running and (self.skip_animation or now >= self.next_move_at):
            if not self.session.step():
                break  # a human still has to choose their own move
            self.next_move_at = now + MOVE_DELAY
            if self.session.state.is_terminal():
                self.running = False
            if not self.skip_animation or time.perf_counter() >= deadline:
                break

    def run(self):
        clock = pygame.time.Clock()
        while True:
            for event in pygame.event.get():
                result = self.handle_event(event)
                if result is not None:
                    return result == "back"
            self.update(pygame.time.get_ticks())
            self.draw()
            clock.tick(60)


if __name__ == "__main__":
    try:
        AdversarialGui().run()
    finally:
        pygame.quit()
