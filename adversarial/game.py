"""The game loop: players alternate until the game is over."""
from collections import namedtuple

from adversarial.state import A, B

# winner: A, B or None for a draw. capped: True if the ply cap ended the game with treasure left.
GameResult = namedtuple("GameResult", ["scores", "plies", "winner", "capped", "paths"])


def play_game(state, players, on_move=None):
    """Run the game from `state` to the end and return a GameResult.

    players: (player_a, player_b). Player A moves first.
    on_move(state, who, before, move, took_treasure, player) is called after every move so a
    caller can log it or redraw the board.
    """
    paths = ([state.pos[A]], [state.pos[B]])  # every cell each agent stood on, in order
    while not state.is_terminal():
        who = state.turn
        player = players[who]
        before = state.pos[who]
        snapshot = state.snapshot()

        move = player.choose(state)

        # a player may look ahead (make/undo) but must hand the state back untouched; if it did
        # not, every later move would be played on a corrupted board, so fail loudly right here
        if state.snapshot() != snapshot:
            raise RuntimeError(f"{player.label} changed the game state while choosing a move")

        treasures_before = len(state.treasures)
        state.play(move)  # the checked version: an illegal move raises instead of being played
        if move is not None:
            paths[who].append(move)
        if on_move is not None:
            on_move(state, who, before, move, len(state.treasures) < treasures_before, player)

    difference = state.scores[A] - state.scores[B]
    winner = A if difference > 0 else B if difference < 0 else None
    return GameResult(tuple(state.scores), state.plies, winner, bool(state.treasures), paths)
