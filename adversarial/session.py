"""One turn at a time for the window, using the same players as the terminal game."""
import random

from adversarial.display import format_move
from adversarial.evaluation import EVALUATIONS
from adversarial.game import GameResult
from adversarial.generator import generate_map
from adversarial.players import RandomPlayer, SearchPlayer
from adversarial.search import AlphaBeta, Minimax
from adversarial.state import GameState

ALGORITHMS = (AlphaBeta, Minimax)
DEPTHS = (2, 4, 6)
MODES = ("AI vs Random", "AI vs AI", "Human vs AI")
EVAL_NAMES = tuple(EVALUATIONS)


class GameSession:
    def __init__(self, seed=None, out=print):
        self.seed = seed if seed is not None else random.randrange(1_000_000)
        self.out = out
        self.mode = MODES[0]
        self.algorithms = [AlphaBeta, AlphaBeta]
        self.depths = [4, 4]
        self.evaluations = [EVAL_NAMES[0], EVAL_NAMES[0]]
        self.compare = False
        self.reset()

    def reset(self, regenerate=False):
        if regenerate:
            self.seed = (self.seed + random.randrange(1, 1_000_000)) % 1_000_000
        self.state = GameState(generate_map(self.seed))
        self.players = [self._make_ai(0), self._make_ai(1)]
        if self.mode == "AI vs Random":
            self.players[1] = RandomPlayer(self.seed)
        elif self.mode == "Human vs AI":
            self.players[1] = None  # the window supplies B's moves
        self.paths = [[position] for position in self.state.pos]
        self.moves = [0, 0]
        self.log = []
        self.last_action = ""
        self.last_pair = None
        self.comparison = {name: {"nodes": 0, "time": 0.0} for name in ("Minimax", "Alpha-Beta")}
        self.out(f"\nGUI map seed {self.seed} | {self.mode} | A moves first")

    def _make_ai(self, who):
        name = self.evaluations[who]
        return SearchPlayer(self.algorithms[who], EVALUATIONS[name], self.depths[who], name.split()[0])

    def is_human_turn(self):
        return not self.state.is_terminal() and self.players[self.state.turn] is None

    def step(self, human_move=None):
        if self.state.is_terminal():
            return False
        who = self.state.turn
        player = self.players[who]
        before = self.state.pos[who]
        snapshot = self.state.snapshot()
        if player is None:
            if human_move is None and self.state.legal_moves() != [None]:
                return False  # wait for a direction or a click; never read terminal input
            move = human_move
            if move not in self.state.legal_moves():
                return False
        else:
            move = player.choose(self.state)
            if self.compare and isinstance(player, SearchPlayer):
                other = Minimax if isinstance(player.searcher, AlphaBeta) else AlphaBeta
                result = other(player.searcher.evaluate, player.searcher.depth).search(self.state)
                if (result.move, result.value) != (player.last.move, player.last.value):
                    raise RuntimeError("Minimax and Alpha-Beta disagreed")
                self.last_pair = {item.algorithm: item for item in (player.last, result)}
                for name, item in self.last_pair.items():
                    self.comparison[name]["nodes"] += item.nodes_expanded
                    self.comparison[name]["time"] += item.elapsed
        if self.state.snapshot() != snapshot:
            raise RuntimeError("The player changed the board while choosing its move")

        took = move in self.state.treasures
        self.state.play(move)
        self.last_action = f"Turn {self.state.plies} | {'AB'[who]}: " + (
            "passes" if move is None else f"{before} -> {move}" + (" + treasure" if took else ""))
        if move is not None:
            self.paths[who].append(move)
            self.moves[who] += 1
        label = player.label if player is not None else "human"
        info = player.last_info() if player is not None else ""
        self.log.append(format_move(self.state.plies, who, label, before, move, took, info))
        self.out(self.log[-1])
        if self.state.is_terminal():
            self.out(self.status())
            for index, path in enumerate(self.paths):
                self.out(f"{'AB'[index]} path: " + " -> ".join(str(cell) for cell in path))
        return True

    def status(self):
        state = self.state
        if state.is_terminal():
            a, b = state.scores
            verdict = "Draw" if a == b else f"{'A' if a > b else 'B'} wins"
            reason = "move limit reached" if state.treasures else "all treasures collected"
            return f"{verdict} - {reason}"
        if self.is_human_turn():
            return "B: your move - arrow keys or click a highlighted cell"
        return f"{'AB'[state.turn]}'s turn"

    def result(self):
        a, b = self.state.scores
        winner = None if a == b else 0 if a > b else 1
        return GameResult(tuple(self.state.scores), self.state.plies, winner,
                          bool(self.state.treasures), tuple(self.paths))

    def pruning_ratio(self):
        plain = self.comparison["Minimax"]["nodes"]
        return 1 - self.comparison["Alpha-Beta"]["nodes"] / plain if plain else None
