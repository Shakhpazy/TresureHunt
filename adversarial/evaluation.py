"""Heuristic evaluation functions: how good is this position for `me`?

The search calls evaluate(state, me) wherever it stops at the depth limit with the game still
unfinished. A positive number means "good for me", negative means "good for the opponent".

Three evaluation functions are provided so the report can compare them. They are built from
the same parts, adding exactly one idea each, so any difference in results can be pinned on
that one idea:

    E1 baseline        treasure lead + distance to the nearest treasure (mine vs theirs)
    E2 baseline + trap E1 + a penalty for standing next to traps
    E3 baseline + race E1 + how many treasures I would reach before the opponent would

Weights are chosen by hand, under one rule that matters more than any individual value:

    TAKING a treasure must always look better than hovering next to it.

A capture adds W_LEAD, but it also removes that treasure from the "nearest treasure" distance,
which can make the next nearest one far away (up to rows + cols - 2 = 28 cells on 15x15).
If W_LEAD were smaller than that jump the agent would circle a treasure forever without taking
it. We saw exactly this with a lead weight of 10. W_LEAD = 100 clears the largest possible
positional swing (distance 28 + race 5 * W_RACE) with a wide margin, and the largest possible
total, 5 * W_LEAD + positional terms, stays below the win value of 1000 so a real win always
beats a guess. Both facts are checked by tests.
"""
from adversarial.state import MAX_PLIES_LIMIT, WIN

W_LEAD = 100  # per treasure of lead: the real objective, so by far the heaviest
W_DIST = 1    # per step of Manhattan distance: a tie-breaker that steers toward treasure
W_RACE = 5    # per treasure I would reach first (about five steps of distance)
W_TRAP = 2    # per trap orthogonally next to an agent (about two steps of distance)

_NEIGHBOURS = ((1, 0), (0, 1), (-1, 0), (0, -1))


def _manhattan(a, b):
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def _nearest(position, treasures):
    return min(_manhattan(position, t) for t in treasures)


def _adjacent_traps(state, position):
    # each orthogonally adjacent trap is one exit this agent cannot use
    r, c = position
    return sum((r + dr, c + dc) in state.traps for dr, dc in _NEIGHBOURS)


def evaluate_baseline(state, me):
    """E1: treasure lead, plus how much closer I am to the nearest treasure than the opponent."""
    opponent = 1 - me
    lead = state.scores[me] - state.scores[opponent]
    if not state.treasures:  # the search never evaluates a finished game, but stay safe
        return W_LEAD * lead
    closeness = _nearest(state.pos[opponent], state.treasures) - _nearest(state.pos[me], state.treasures)
    return W_LEAD * lead + W_DIST * closeness


def evaluate_trap(state, me):
    """E2: E1 plus a penalty for standing next to traps (and a bonus for the opponent doing so)."""
    opponent = 1 - me
    exposure = _adjacent_traps(state, state.pos[opponent]) - _adjacent_traps(state, state.pos[me])
    return evaluate_baseline(state, me) + W_TRAP * exposure


def evaluate_race(state, me):
    """E3: E1 plus the treasure race.

    For every remaining treasure, whoever is strictly closer (Manhattan) is the likely
    collector. A treasure that is equally far from both counts for nobody. The term is
    (treasures I am closer to) - (treasures they are closer to).
    """
    opponent = 1 - me
    race = 0
    for treasure in state.treasures:
        mine = _manhattan(state.pos[me], treasure)
        theirs = _manhattan(state.pos[opponent], treasure)
        if mine < theirs:
            race += 1
        elif theirs < mine:
            race -= 1
    return evaluate_baseline(state, me) + W_RACE * race


EVALUATIONS = {
    "E1 baseline": evaluate_baseline,
    "E2 baseline+trap": evaluate_trap,
    "E3 baseline+race": evaluate_race,
}

# The most any evaluation can return in magnitude: 5 treasures of lead, the largest possible
# distance term on a 15x15 board, the largest race term, and four traps of exposure each.
MAX_ABS_EVALUATION = 5 * W_LEAD + W_DIST * 28 + W_RACE * 5 + W_TRAP * 8
# the worst win a finished game can score is WIN - MAX_PLIES_LIMIT (a win right at the cap)
assert MAX_ABS_EVALUATION < WIN - MAX_PLIES_LIMIT, "heuristic values must stay below any real win"
