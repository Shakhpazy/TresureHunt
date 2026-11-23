"""Minimax and Alpha-Beta pruning over a GameState.

Both searches pick a move for whoever is to move at the root ("me") and evaluate every
position from me's point of view: positions where it is my turn are MAX nodes, positions
where it is the opponent's turn are MIN nodes. Which kind of node it is comes from
state.turn, never from the depth, so the search keeps working even if a pass appears.

`evaluate(state, player)` is the heuristic used where the search stops at the depth limit.
It must return a number from `player`'s point of view, strictly between LOSS and WIN, so a
real win always beats any heuristic guess.

depth counts plies (one ply = one agent's move), so depth 6 is three moves each.
"""
import time
from collections import namedtuple

INF = float("inf")

SearchResult = namedtuple(
    "SearchResult",
    ["move", "value", "nodes_expanded", "cutoffs", "elapsed", "depth", "algorithm"],
)


class _Searcher:
    name = ""
    prunes = False  # Alpha-Beta narrows the root's alpha as it finds better moves

    def __init__(self, evaluate, depth):
        if not callable(evaluate):
            raise TypeError("evaluate must be a function (state, player) -> number")
        if not isinstance(depth, int) or isinstance(depth, bool) or depth < 1:
            raise ValueError(f"depth must be an integer of at least 1, got {depth!r}")
        self.evaluate = evaluate
        self.depth = depth

    def search(self, state):
        if state.is_terminal():
            raise ValueError("the game is over, there is no move to choose")

        self.me = state.turn
        self.nodes = 0
        self.cutoffs = 0
        start = time.perf_counter()

        best_value, best_move = -INF, None
        alpha = -INF
        for move in state.legal_moves():
            token = state.make(move)
            try:
                value = self._value(state, self.depth - 1, alpha, INF)
            finally:
                # runs even if evaluate() raised, so a crash can never leave the caller's
                # shared state stuck halfway through a hypothetical move
                state.undo(token)
            # strict ">": on a tie the FIRST move in legal_moves() order wins, which keeps
            # the choice deterministic (and identical between Minimax and Alpha-Beta)
            if value > best_value:
                best_value, best_move = value, move
            if self.prunes and best_value > alpha:
                alpha = best_value

        elapsed = time.perf_counter() - start
        # the root itself is one expanded node as well
        return SearchResult(
            best_move, best_value, self.nodes + 1, self.cutoffs, elapsed, self.depth, self.name
        )

    def _value(self, state, depth, alpha, beta):
        raise NotImplementedError


class Minimax(_Searcher):
    name = "Minimax"

    def _value(self, state, depth, alpha, beta):
        # alpha and beta are accepted only so both searches share one signature; plain
        # Minimax never looks at them
        self.nodes += 1
        if state.is_terminal():
            return state.utility(self.me)
        if depth == 0:
            return self.evaluate(state, self.me)

        maximizing = state.turn == self.me
        best = -INF if maximizing else INF
        for move in state.legal_moves():
            token = state.make(move)
            try:
                value = self._value(state, depth - 1, alpha, beta)
            finally:
                state.undo(token)
            best = max(best, value) if maximizing else min(best, value)
        return best


class AlphaBeta(_Searcher):
    name = "Alpha-Beta"
    prunes = True

    def _value(self, state, depth, alpha, beta):
        # alpha: the best score MAX is already guaranteed on the path to this node
        # beta:  the best score MIN is already guaranteed on the path to this node
        self.nodes += 1
        if state.is_terminal():
            return state.utility(self.me)
        if depth == 0:
            return self.evaluate(state, self.me)

        maximizing = state.turn == self.me
        best = -INF if maximizing else INF
        for move in state.legal_moves():
            token = state.make(move)
            try:
                value = self._value(state, depth - 1, alpha, beta)
            finally:
                state.undo(token)

            if maximizing:
                best = max(best, value)
                alpha = max(alpha, best)
            else:
                best = min(best, value)
                beta = min(beta, best)

            if alpha >= beta:
                # MIN above would never let the game reach this node (or MAX above would
                # never allow it, symmetrically), so the remaining siblings cannot matter
                self.cutoffs += 1
                break
        return best
