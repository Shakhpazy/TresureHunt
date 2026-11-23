from adversarial.generator import GameMap
from adversarial.state import GameState
from grid import EMPTY, STATIC_WALLS, TRAP, TREASURE

SYMBOLS = {"#": STATIC_WALLS, "X": TRAP, "T": TREASURE, ".": EMPTY, "A": EMPTY, "B": EMPTY}


def make_state(*rows, max_plies=200):
    """Build a GameState from text rows: # wall, X trap, T treasure, . empty, A and B the agents."""
    grid = [[SYMBOLS[symbol] for symbol in row] for row in rows]
    starts = {}
    for r, row in enumerate(rows):
        for c, symbol in enumerate(row):
            if symbol in "AB":
                starts[symbol] = (r, c)
    return GameState(GameMap(grid, starts["A"], starts["B"], seed=None), max_plies=max_plies)


def manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def simple_eval(state, me):
    """A deliberately plain, tie-heavy evaluation used only to test the search machinery."""
    opponent = 1 - me
    lead = state.scores[me] - state.scores[opponent]
    if not state.treasures:
        return 10 * lead
    nearest_me = min(manhattan(state.pos[me], t) for t in state.treasures)
    nearest_opponent = min(manhattan(state.pos[opponent], t) for t in state.treasures)
    return 10 * lead - nearest_me + nearest_opponent
