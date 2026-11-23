"""Who chooses the moves: a random agent, a search agent (Minimax / Alpha-Beta) or a human.

Every player has the same small interface so the game loop never needs to know which kind
it is talking to:
    label        short description for the log, e.g. "Alpha-Beta d4 E1"
    choose(state) -> a move taken from state.legal_moves()   (must NOT change the state)
    last_info()  -> text about the move just chosen, or ""
"""
import random

from adversarial.state import PASS


class GameAborted(Exception):
    """The human quit (typed q, pressed Ctrl-D) before the game was over."""


class RandomPlayer:
    label = "random"

    def __init__(self, seed=None):
        # a private generator: with a seed, the same game replays identically
        self.rng = random.Random(seed)

    def choose(self, state):
        return self.rng.choice(state.legal_moves())

    def last_info(self):
        return ""


class SearchPlayer:
    """Chooses moves with Minimax or Alpha-Beta, and keeps running totals of the work done."""

    def __init__(self, algorithm, evaluate, depth, eval_name=""):
        self.searcher = algorithm(evaluate, depth)  # validates evaluate and depth
        self.label = " ".join(part for part in (algorithm.name, f"d{depth}", eval_name) if part)
        self.searches = 0
        self.nodes_expanded = 0
        self.cutoffs = 0
        self.elapsed = 0.0
        self.last = None

    def choose(self, state):
        result = self.searcher.search(state)
        self.last = result
        self.searches += 1
        self.nodes_expanded += result.nodes_expanded
        self.cutoffs += result.cutoffs
        self.elapsed += result.elapsed
        return result.move

    def last_info(self):
        r = self.last
        if r is None:
            return ""
        text = f"value={r.value} nodes={r.nodes_expanded}"
        if r.algorithm != "Minimax":
            text += f" cutoffs={r.cutoffs}"
        return text + f" time={r.elapsed * 1000:.2f}ms"


# the four moves a human can type, matching the board: u = up (row - 1), d = down (row + 1)
HUMAN_KEYS = {"u": (-1, 0), "d": (1, 0), "l": (0, -1), "r": (0, 1)}


class HumanPlayer:
    label = "human"

    def __init__(self, input_fn=input, out=print):
        self.input_fn = input_fn
        self.out = out

    def choose(self, state):
        legal = state.legal_moves()
        if legal == [PASS]:
            self.out("You have no legal move, so you pass.")
            return PASS

        row, col = state.pos[state.turn]
        options = {
            key: (row + dr, col + dc)
            for key, (dr, dc) in HUMAN_KEYS.items()
            if (row + dr, col + dc) in legal
        }
        prompt = f"Your move [{'/'.join(sorted(options))}], q to quit: "
        while True:
            try:
                text = self.input_fn(prompt).strip().lower()
            except EOFError:  # input closed (Ctrl-D or piped input ran out): stop, do not loop forever
                raise GameAborted from None
            if text == "q":
                raise GameAborted
            if text in options:
                return options[text]
            # anything else: say why and ask again, never crash and never guess
            blocked = "that way is blocked" if text in HUMAN_KEYS else f"{text!r} is not a move"
            self.out(f"{blocked}. Choose one of: {', '.join(sorted(options))}.")

    def last_info(self):
        return ""
