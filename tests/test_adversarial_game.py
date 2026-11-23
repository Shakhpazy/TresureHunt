import pytest

from adversarial.game import play_game
from adversarial.generator import generate_map
from adversarial.players import RandomPlayer, SearchPlayer
from adversarial.search import AlphaBeta
from adversarial.state import A, B, GameState
from tests.adversarial_helpers import make_state, simple_eval


def test_a_full_game_ends_with_a_consistent_result():
    for seed in range(10):
        state = GameState(generate_map(seed))
        total = len(state.treasures)
        result = play_game(state, (RandomPlayer(seed), RandomPlayer(seed + 100)))
        assert state.is_terminal()
        assert result.plies == state.plies
        if not result.capped:
            assert sum(result.scores) == total  # every treasure went to someone
        expected = A if result.scores[A] > result.scores[B] else B if result.scores[B] > result.scores[A] else None
        assert result.winner == expected


def test_paths_record_every_cell_each_agent_stood_on():
    state = make_state("A.T.B")
    result = play_game(state, (SearchPlayer(AlphaBeta, simple_eval, 4), RandomPlayer(1)))
    assert result.paths[A][0] == (0, 0)
    assert result.paths[B][0] == (0, 4)
    assert result.paths[A][-1] == state.pos[A] and result.paths[B][-1] == state.pos[B]
    for path in result.paths:
        for (r1, c1), (r2, c2) in zip(path, path[1:]):
            assert abs(r1 - r2) + abs(c1 - c2) == 1


def test_on_move_is_called_once_per_ply_and_reports_treasure_pickups():
    seen = []
    state = make_state("A.T.B")
    play_game(state, (SearchPlayer(AlphaBeta, simple_eval, 4), RandomPlayer(1)),
              on_move=lambda s, who, before, move, took, player: seen.append((s.plies, who, took)))
    assert [p for p, _, _ in seen] == list(range(1, len(seen) + 1))
    assert sum(took for _, _, took in seen) == 1  # exactly one treasure on this board


def test_a_game_that_hits_the_cap_is_flagged_and_decided_by_score():
    state = make_state(
        "A#T",
        "#.#",
        "B..",
        max_plies=6,
    )
    state.scores = [1, 0]  # pretend A already scored: the treasure is unreachable for A
    result = play_game(state, (RandomPlayer(1), RandomPlayer(2)))
    assert result.plies == 6 and result.capped


class Cheater:
    label = "cheater"

    def choose(self, state):
        state.make(state.legal_moves()[0])  # changes the board and never undoes it
        return None

    def last_info(self):
        return ""


class Teleporter:
    label = "teleporter"

    def choose(self, state):
        return (0, 0)  # not a legal move for anybody standing elsewhere

    def last_info(self):
        return ""


def test_a_player_that_corrupts_the_state_is_caught_immediately():
    state = make_state("A.T.B")
    with pytest.raises(RuntimeError, match="cheater changed the game state"):
        play_game(state, (Cheater(), RandomPlayer(1)))


def test_an_illegal_move_is_rejected_not_played():
    state = make_state("A.T.B")
    with pytest.raises(ValueError, match="illegal"):
        play_game(state, (RandomPlayer(1), Teleporter()))
