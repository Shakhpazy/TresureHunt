import random

import pytest

from adversarial.generator import generate_map
from adversarial.state import A, B, DRAW, LOSS, PASS, WIN, GameState
from tests.adversarial_helpers import make_state


def test_legal_moves_follow_down_right_up_left_order():
    state = make_state(
        ".....",
        ".....",
        "..A..",
        ".....",
        "....B",
    )
    assert state.legal_moves() == [(3, 2), (2, 3), (1, 2), (2, 1)]


def test_walls_traps_edges_and_the_other_agent_are_not_legal():
    state = make_state(
        "A#",
        "XB",
    )
    # right is a wall, down is a trap, up and left are off the board
    assert state.legal_moves() == [PASS]

    state = make_state(
        "AB.",
        "...",
    )
    # B stands on the right, so A can only go down
    assert state.legal_moves() == [(1, 0)]


def test_a_boxed_in_agent_passes_and_turns_keep_alternating():
    state = make_state(
        "A#.T",
        "#..B",
    )
    assert state.legal_moves() == [PASS]
    state.make(PASS)
    assert state.turn == B and state.plies == 1
    assert state.legal_moves() != [PASS]


def test_collecting_a_treasure_scores_and_removes_it_and_undo_restores_it():
    state = make_state("AT.B")
    before = state.snapshot()
    token = state.make((0, 1))
    assert state.scores == [1, 0]
    assert (0, 1) not in state.treasures
    assert state.pos[A] == (0, 1)
    assert state.turn == B
    state.undo(token)
    assert state.snapshot() == before


def test_random_playouts_can_be_undone_exactly():
    for seed in range(30):
        state = GameState(generate_map(seed))
        start = state.snapshot()
        rng = random.Random(seed)
        tokens = []
        while not state.is_terminal() and len(tokens) < 150:
            tokens.append(state.make(rng.choice(state.legal_moves())))
        for token in reversed(tokens):
            state.undo(token)
        assert state.snapshot() == start


def test_agents_never_share_a_cell_or_enter_blocked_cells_in_random_play():
    for seed in range(20):
        state = GameState(generate_map(seed))
        rng = random.Random(seed)
        while not state.is_terminal():
            state.make(rng.choice(state.legal_moves()))
            assert state.pos[A] != state.pos[B]
            for pos in state.pos:
                assert pos not in state.blocked


def test_a_non_square_board_uses_its_real_width_and_height():
    state = make_state("A.TB")  # 1 row, 4 columns: a square-only bounds check would break this
    assert state.legal_moves() == [(0, 1)]


def test_undo_out_of_order_raises_instead_of_corrupting():
    state = make_state("A..BT")
    first = state.make((0, 1))
    state.make((0, 2))
    with pytest.raises(ValueError, match="out of order"):
        state.undo(first)


def test_play_rejects_illegal_moves_and_moves_after_the_game_ends():
    state = make_state(
        "A#T",
        ".B.",
    )
    before = state.snapshot()
    with pytest.raises(ValueError, match="illegal"):
        state.play((0, 1))      # a wall
    with pytest.raises(ValueError, match="illegal"):
        state.play((5, 5))      # off the board
    assert state.snapshot() == before  # a rejected move changes nothing

    finished = make_state("AT.B")
    finished.play((0, 1))
    assert finished.is_terminal()
    with pytest.raises(ValueError, match="over"):
        finished.play((0, 2))


def test_game_ends_when_all_treasures_are_gone():
    state = make_state("ATB")
    assert not state.is_terminal()
    state.make((0, 1))
    assert state.is_terminal()


def test_game_ends_at_the_ply_cap():
    state = make_state("A.T.B", max_plies=2)
    state.make((0, 1))
    assert not state.is_terminal()
    state.make((0, 3))
    assert state.is_terminal()


def test_utility_is_win_loss_or_draw_by_treasure_count():
    state = make_state("A..B")
    state.scores = [2, 1]
    assert state.utility(A) == WIN and state.utility(B) == LOSS
    state.scores = [1, 1]
    assert state.utility(A) == DRAW and state.utility(B) == DRAW
