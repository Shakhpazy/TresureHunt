"""The game state: the thing Minimax searches through.

One mutable GameState is shared by the whole search. To look at a child position the
search calls make(move), which changes the state in place and returns an undo token, then
calls undo(token) to put everything back. That is far cheaper than copying the board at
every node, but it only works if every make is matched by exactly one undo, in
last-in-first-out order. undo() checks this and raises instead of silently corrupting.
"""
from algos.bfs import BFS  # reused only for its direction order: DOWN, RIGHT, UP, LEFT
from grid import STATIC_WALLS, TRAP, TREASURE

A, B = 0, 1          # player indexes: A moves first
PASS = None          # the one "move" of an agent that has nowhere to go
DIRECTIONS = BFS.DIRECTIONS
BLOCKED_CELLS = (STATIC_WALLS, TRAP)  # traps behave exactly like walls in this game

MAX_PLIES = 200      # safety cap: a ply is one agent's move
MAX_PLIES_LIMIT = 400  # the largest cap allowed: see utility() for why there must be a limit
WIN, LOSS, DRAW = 1000, -1000, 0  # base utilities of a finished game, see utility()


class GameState:

    def __init__(self, game_map, max_plies=MAX_PLIES):
        if not isinstance(max_plies, int) or isinstance(max_plies, bool) or not 1 <= max_plies <= MAX_PLIES_LIMIT:
            raise ValueError(f"max_plies must be an integer from 1 to {MAX_PLIES_LIMIT}, got {max_plies!r}")
        self.grid = game_map.grid  # never modified: walls, traps and the starting treasures
        self.rows = len(self.grid)
        self.cols = len(self.grid[0])
        self.blocked = {
            (r, c)
            for r, row in enumerate(self.grid)
            for c, cell in enumerate(row)
            if cell in BLOCKED_CELLS
        }
        self.traps = frozenset(
            (r, c) for r, row in enumerate(self.grid) for c, cell in enumerate(row) if cell == TRAP
        )
        self.treasures = {
            (r, c) for r, row in enumerate(self.grid) for c, cell in enumerate(row) if cell == TREASURE
        }
        self.total_treasures = len(self.treasures)
        self.pos = [game_map.start_a, game_map.start_b]
        self.scores = [0, 0]
        self.turn = A
        self.plies = 0
        self.max_plies = max_plies

    # ---- reading the state -------------------------------------------------------------

    def legal_moves(self):
        """Cells the player to move can step to, in a fixed order; [PASS] if there are none.

        Walls, traps, the board edge and the other agent's cell are all unavailable. Returning
        [PASS] instead of [] keeps turns strictly alternating and means the search never has
        to handle "no moves" as a special case.
        """
        r, c = self.pos[self.turn]
        other = self.pos[1 - self.turn]
        moves = []
        for dr, dc in DIRECTIONS:
            nxt = (r + dr, c + dc)
            if (
                0 <= nxt[0] < self.rows and 0 <= nxt[1] < self.cols
                and nxt not in self.blocked
                and nxt != other
            ):
                moves.append(nxt)
        return moves or [PASS]

    def is_terminal(self):
        return not self.treasures or self.plies >= self.max_plies

    def utility(self, player):
        """Result of a finished game from `player`'s point of view.

        A win is worth WIN minus the plies played, a loss LOSS plus the plies played, a draw
        0. So a faster win beats a slower win, and a slower loss beats a faster loss.

        Why not a flat WIN? Once a player has clinched the game, a flat value makes "capture
        now" and "capture three moves from now" tie, and a depth-limited search can always see
        a catch-up later, so it procrastinates forever (seen in testing: a deeper search stalled
        MORE often). Rewarding speed breaks the tie in favour of finishing.

        Every win is still worth at least WIN - MAX_PLIES_LIMIT, which stays above any
        heuristic evaluation (evaluation.py checks this), so a real result always beats a guess.
        """
        difference = self.scores[player] - self.scores[1 - player]
        if difference > 0:
            return WIN - self.plies
        if difference < 0:
            return LOSS + self.plies
        return DRAW

    def snapshot(self):
        """Everything that make/undo is allowed to change, as a comparable value (for tests)."""
        return (tuple(self.pos), tuple(self.scores), frozenset(self.treasures), self.turn, self.plies)

    # ---- changing the state ------------------------------------------------------------

    def make(self, move):
        """Apply `move` for the player to move and return the token that undoes it.

        Unchecked on purpose (the search only passes moves from legal_moves(), and checking
        would double the cost of every node). Anything coming from outside the search, such
        as a human typing a move, must go through play().
        """
        player = self.turn
        old_pos = self.pos[player]
        collected = False
        if move is not PASS:
            self.pos[player] = move
            if move in self.treasures:
                self.treasures.remove(move)
                self.scores[player] += 1
                collected = True
        self.turn = 1 - player
        self.plies += 1
        return (player, old_pos, move, collected)

    def undo(self, token):
        player, old_pos, move, collected = token
        if self.turn != 1 - player:
            raise ValueError("undo() called out of order: tokens must be undone last-in, first-out")
        self.plies -= 1
        self.turn = player
        if collected:
            self.treasures.add(move)
            self.scores[player] -= 1
        self.pos[player] = old_pos

    def play(self, move):
        """Checked version of make() for moves that did not come from legal_moves()."""
        if self.is_terminal():
            raise ValueError("the game is over")
        if move not in self.legal_moves():
            raise ValueError(f"illegal move {move} for player {'AB'[self.turn]} at {self.pos[self.turn]}")
        return self.make(move)
