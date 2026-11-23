import pytest

from adversarial.generator import generate_map
from adversarial.players import GameAborted, HumanPlayer, RandomPlayer, SearchPlayer
from adversarial.search import AlphaBeta, Minimax
from adversarial.state import PASS, GameState
from tests.adversarial_helpers import make_state, simple_eval


def test_random_player_only_picks_legal_moves_and_replays_with_a_seed():
    state = GameState(generate_map(4))
    first, second = RandomPlayer(seed=9), RandomPlayer(seed=9)
    for _ in range(50):
        move = first.choose(state)
        assert move in state.legal_moves()
        assert second.choose(state) == move  # same seed, same choices


def test_search_player_chooses_the_search_move_and_totals_its_work():
    state = GameState(generate_map(2))
    player = SearchPlayer(AlphaBeta, simple_eval, depth=4, eval_name="E")
    assert player.label == "Alpha-Beta d4 E"

    expected = AlphaBeta(simple_eval, 4).search(state)
    assert player.choose(state) == expected.move
    assert player.choose(state) == expected.move
    assert player.searches == 2
    assert player.nodes_expanded == 2 * expected.nodes_expanded
    assert player.cutoffs == 2 * expected.cutoffs
    assert "cutoffs=" in player.last_info() and "nodes=" in player.last_info()
    assert "cutoffs=" not in SearchPlayer(Minimax, simple_eval, 2).last_info()


def test_search_player_rejects_a_bad_depth_at_construction():
    with pytest.raises(ValueError):
        SearchPlayer(AlphaBeta, simple_eval, depth=0)


class Scripted:
    """Stand-in for input(): hands out the given answers and records each prompt."""

    def __init__(self, *answers):
        self.answers = list(answers)
        self.prompts = []

    def __call__(self, prompt):
        self.prompts.append(prompt)
        if not self.answers:
            raise EOFError
        return self.answers.pop(0)


def human(*answers):
    typed, shown = Scripted(*answers), []
    return HumanPlayer(typed, shown.append), typed, shown


def test_human_types_a_direction_and_gets_the_matching_cell():
    state = make_state(
        ".....",
        "..A..",
        ".....",
        "....T",
        "....B",
    )
    for key, cell in {"u": (0, 2), "d": (2, 2), "l": (1, 1), "r": (1, 3)}.items():
        player, _, _ = human(key)
        assert player.choose(state) == cell


def test_human_is_reprompted_on_garbage_and_blocked_directions_without_crashing():
    state = make_state(
        "A#..T",
        "...B.",
    )
    # right of A is a wall, up is off the board, "x" and "" are not moves, " D " is fine
    player, typed, shown = human("r", "u", "x", "", " D ")
    assert player.choose(state) == (1, 0)
    assert len(typed.prompts) == 5
    assert any("blocked" in message for message in shown)
    assert any("not a move" in message for message in shown)


def test_human_quitting_or_closed_input_aborts_cleanly():
    state = make_state("A.TB")
    with pytest.raises(GameAborted):
        human("q")[0].choose(state)
    with pytest.raises(GameAborted):
        human()[0].choose(state)  # input ran out (Ctrl-D): must not loop forever


def test_human_with_no_legal_move_passes_without_asking():
    state = make_state(
        "A#.T",
        "#..B",
    )
    player, typed, shown = human()
    assert player.choose(state) is PASS
    assert typed.prompts == [] and any("pass" in message for message in shown)
