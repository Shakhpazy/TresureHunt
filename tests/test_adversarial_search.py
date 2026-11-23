import random

import pytest

from adversarial.generator import generate_map
from adversarial.search import AlphaBeta, Minimax
from adversarial.state import LOSS, WIN, GameState
from tests.adversarial_helpers import make_state, simple_eval


def test_takes_an_adjacent_treasure():
    state = make_state(".AT...B")
    result = Minimax(simple_eval, depth=2).search(state)
    assert result.move == (0, 2)


def test_blocks_by_racing_when_the_opponent_would_win_the_treasure():
    # one treasure, both agents are 2 steps from it, A moves first: A wins the race
    state = make_state("A.T.B")
    result = Minimax(simple_eval, depth=4).search(state)
    assert result.move == (0, 1)
    assert result.value == WIN - 3  # A steps, B steps, A captures: the game ends on ply 3


def test_depth_decides_how_far_ahead_a_lost_race_is_visible():
    # the only treasure is 3 steps from A and 2 steps from B, A to move, in a 1-wide corridor:
    # B captures it on ply 4 whatever A does. Depth 4 sees that loss; depth 2 cannot.
    state = make_state("A..T.B")
    assert Minimax(simple_eval, depth=4).search(state).value == LOSS + 4
    assert AlphaBeta(simple_eval, depth=4).search(state).value == LOSS + 4
    assert Minimax(simple_eval, depth=2).search(state).value > LOSS + 4


def test_a_clinched_agent_takes_the_adjacent_treasure_instead_of_procrastinating():
    # A already leads 2-0 and the last treasure is next to it, so the game is won whatever
    # happens. With a flat win value, every move still "wins within the horizon", the first
    # one in move order (down, away from the treasure) was chosen, and A never finished.
    state = make_state(
        "....B",
        "....T",
        "....A",
        ".....",
        ".....",
    )
    state.scores = [2, 0]
    for algorithm in (Minimax, AlphaBeta):
        for depth in (2, 4, 6):
            result = algorithm(simple_eval, depth).search(state)
            assert result.move == (1, 4), (algorithm.__name__, depth)
            assert result.value == WIN - 1


def test_a_faster_win_is_worth_more_and_a_slower_loss_is_worth_more():
    # the corridor race from above, but A needs 3 moves and wins either way (B can't interfere)
    state = make_state(
        "A.T",
        "...",
        "..B",
    )
    state.scores = [1, 0]  # clinched: whatever happens A wins, so only speed can separate moves
    result = Minimax(simple_eval, depth=6).search(state)
    assert result.move == (0, 1)       # heads straight for the treasure
    assert result.value == WIN - 3     # and finishes on ply 3

    # the same logic in reverse: a lost game is better the longer it lasts
    lost = make_state("A..T.B")
    assert Minimax(simple_eval, depth=4).search(lost).value == LOSS + 4


def test_search_leaves_the_state_exactly_as_it_found_it():
    for algorithm in (Minimax, AlphaBeta):
        state = GameState(generate_map(3))
        before = state.snapshot()
        algorithm(simple_eval, depth=4).search(state)
        assert state.snapshot() == before


def test_a_crashing_evaluation_cannot_corrupt_the_state():
    calls = {"n": 0}

    def exploding_eval(state, me):
        calls["n"] += 1
        if calls["n"] == 25:
            raise RuntimeError("boom")
        return 0

    for algorithm in (Minimax, AlphaBeta):
        calls["n"] = 0
        state = GameState(generate_map(3))
        before = state.snapshot()
        with pytest.raises(RuntimeError, match="boom"):
            algorithm(exploding_eval, depth=4).search(state)
        assert state.snapshot() == before


def test_bad_arguments_fail_loudly():
    for depth in (0, -2, 1.5, "4", True, None):
        with pytest.raises(ValueError):
            Minimax(simple_eval, depth=depth)
    with pytest.raises(TypeError):
        AlphaBeta("not callable", depth=2)

    finished = make_state("ATB")
    finished.make((0, 1))
    with pytest.raises(ValueError, match="over"):
        Minimax(simple_eval, depth=2).search(finished)


def test_a_boxed_in_agent_searches_to_a_pass():
    state = make_state(
        "A#.T",
        "#..B",
    )
    result = AlphaBeta(simple_eval, depth=3).search(state)
    assert result.move is None


def test_the_player_to_move_is_always_the_maximizer_even_for_agent_b():
    state = make_state("A...TB")
    state.make((0, 1))  # A steps right, now it is B's turn, with the treasure right next to B
    for algorithm in (Minimax, AlphaBeta):
        result = algorithm(simple_eval, depth=2).search(state)
        assert result.move == (0, 4)  # B takes it
        assert result.value == WIN - 2  # a win from B's own point of view, on ply 2


def random_midgame_state(seed):
    state = GameState(generate_map(seed))
    rng = random.Random(seed)
    for _ in range(rng.randrange(0, 40)):
        if state.is_terminal():
            break
        state.make(rng.choice(state.legal_moves()))
    return state


def test_alpha_beta_matches_minimax_on_many_states_and_depths():
    """Pruning must change how much work is done, never the answer."""
    checked = 0
    for seed in range(60):
        state = random_midgame_state(seed)
        if state.is_terminal():
            continue
        for depth in (1, 2, 3, 4):
            plain = Minimax(simple_eval, depth).search(state)
            pruned = AlphaBeta(simple_eval, depth).search(state)
            assert (pruned.value, pruned.move) == (plain.value, plain.move), (seed, depth)
            assert pruned.nodes_expanded <= plain.nodes_expanded
            checked += 1
    assert checked > 200


def test_alpha_beta_matches_minimax_with_a_trivial_all_ties_evaluation():
    # every non-terminal position scores 0: the worst case for tie-breaking disagreements
    def flat(state, me):
        return 0

    for seed in range(30):
        state = random_midgame_state(seed)
        if state.is_terminal():
            continue
        for depth in (2, 3, 4):
            plain = Minimax(flat, depth).search(state)
            pruned = AlphaBeta(flat, depth).search(state)
            assert (pruned.value, pruned.move) == (plain.value, plain.move), (seed, depth)


def test_alpha_beta_really_prunes_at_depth_4():
    state = GameState(generate_map(1))
    plain = Minimax(simple_eval, 4).search(state)
    pruned = AlphaBeta(simple_eval, 4).search(state)
    assert pruned.cutoffs > 0
    assert pruned.nodes_expanded < plain.nodes_expanded
    assert plain.cutoffs == 0


def test_minimax_node_count_matches_the_tree_size_by_hand():
    # open board, nobody near the treasure: with depth 2 the tree is the root, each of A's
    # moves, and each of B's replies to each of those, which we can count by hand
    state = make_state(
        ".....",
        "..A..",
        ".....",
        "..B..",
        "....T",
    )
    a_moves = state.legal_moves()
    expected = 1
    for move in a_moves:
        token = state.make(move)
        expected += 1 + len(state.legal_moves())
        state.undo(token)
    assert Minimax(simple_eval, depth=2).search(state).nodes_expanded == expected
