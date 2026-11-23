import random

from adversarial.evaluation import (
    EVALUATIONS, MAX_ABS_EVALUATION, W_DIST, W_LEAD, W_RACE, W_TRAP,
    evaluate_baseline, evaluate_race, evaluate_trap,
)
from adversarial.generator import generate_map
from adversarial.state import A, B, WIN, GameState
from tests.adversarial_helpers import make_state


def random_states(count=150):
    for seed in range(count):
        state = GameState(generate_map(seed))
        rng = random.Random(seed)
        for _ in range(rng.randrange(0, 60)):
            if state.is_terminal():
                break
            state.make(rng.choice(state.legal_moves()))
        if not state.is_terminal():
            yield state


def test_baseline_rewards_a_treasure_lead_and_being_closer():
    state = make_state(
        "A..T.B",
    )
    # A is 3 from the treasure, B is 2: B is closer, so A is worse off by exactly W_DIST * 1
    assert evaluate_baseline(state, A) == -W_DIST
    assert evaluate_baseline(state, B) == W_DIST

    state.scores = [1, 0]
    assert evaluate_baseline(state, A) == W_LEAD - W_DIST


def test_trap_term_penalises_standing_next_to_traps():
    near = make_state(
        "XA...",
        ".....",
        "....T",
        "....B",
    )
    far = make_state(
        "X....",
        "..A..",
        "....T",
        "....B",
    )
    # same distances either way is not guaranteed, so compare the trap term on its own
    exposure_near = evaluate_trap(near, A) - evaluate_baseline(near, A)
    exposure_far = evaluate_trap(far, A) - evaluate_baseline(far, A)
    assert exposure_near == -W_TRAP
    assert exposure_far == 0


def test_trap_term_counts_both_agents_and_each_adjacent_trap():
    state = make_state(
        "XAX.T",
        "....B",
    )
    # A has two adjacent traps (left and right), B has none
    assert evaluate_trap(state, A) - evaluate_baseline(state, A) == -2 * W_TRAP
    # the same position seen from B's side: the opponent being exposed is good for B
    assert evaluate_trap(state, B) - evaluate_baseline(state, B) == 2 * W_TRAP


def test_race_term_counts_who_is_strictly_closer_to_each_treasure():
    state = make_state(
        "A.T.TB",   # treasure at col 2 is closer to A, col 4 is closer to B
    )
    assert evaluate_race(state, A) - evaluate_baseline(state, A) == 0  # one each

    state = make_state(
        "A.TTTB",
    )
    # A at col 0 is 2, 3, 4 away from the treasures; B at col 5 is 3, 2, 1 away.
    # A is closer to the first treasure only; B is closer to the other two.
    assert evaluate_race(state, A) - evaluate_baseline(state, A) == W_RACE * (1 - 2)

    tie = make_state("A.T.B")  # one treasure exactly between them: counts for nobody
    assert evaluate_race(tie, A) - evaluate_baseline(tie, A) == 0


def test_every_evaluation_is_zero_sum_between_the_two_players():
    for state in random_states():
        for name, evaluate in EVALUATIONS.items():
            assert evaluate(state, A) == -evaluate(state, B), name


def test_evaluations_stay_below_the_value_of_a_real_win():
    biggest = 0
    for state in random_states():
        for evaluate in EVALUATIONS.values():
            for me in (A, B):
                biggest = max(biggest, abs(evaluate(state, me)))
    assert biggest <= MAX_ABS_EVALUATION < WIN


def test_taking_a_treasure_always_beats_not_taking_it_one_move_ahead():
    """The weight rule from evaluation.py: no positional gain may outweigh a capture."""
    checked = 0
    for state in random_states():
        me = state.turn
        captures, others = [], []
        for move in state.legal_moves():
            if move is None:
                continue
            token = state.make(move)
            for name, evaluate in EVALUATIONS.items():
                value = evaluate(state, me) if state.treasures else None
                if value is None:
                    continue  # the capture ended the game; the search scores that as a win
                (captures if token[3] else others).append((name, value))
            state.undo(token)
        for name in EVALUATIONS:
            best_capture = [v for n, v in captures if n == name]
            best_other = [v for n, v in others if n == name]
            if best_capture and best_other:
                assert min(best_capture) > max(best_other), name
                checked += 1
    assert checked > 0
