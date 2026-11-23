import pygame
import pytest

from adversarial.game import play_game
from adversarial.gui import AdversarialGui, MOVE_DELAY
from adversarial.session import GameSession
from adversarial.search import AlphaBeta, Minimax
from gui import Gui
from tests.adversarial_helpers import make_state


@pytest.mark.parametrize("mode", ["AI vs Random", "AI vs AI"])
@pytest.mark.parametrize("algorithm", [Minimax, AlphaBeta])
def test_step_session_matches_the_terminal_game(mode, algorithm):
    window_game = GameSession(2, out=lambda text: None)
    window_game.mode = mode
    window_game.algorithms = [algorithm, AlphaBeta]
    window_game.depths = [2, 4]
    window_game.reset()
    terminal_game = GameSession(2, out=lambda text: None)
    terminal_game.mode = mode
    terminal_game.algorithms = [algorithm, AlphaBeta]
    terminal_game.depths = [2, 4]
    terminal_game.reset()
    expected = play_game(terminal_game.state, terminal_game.players)
    while not window_game.state.is_terminal():
        assert window_game.step()
    assert window_game.result() == expected
    assert not window_game.step()


def test_comparison_uses_the_same_position_and_reset_replays_it():
    game = GameSession(3, out=lambda text: None)
    initial = game.state.snapshot()
    game.compare = True
    game.step()
    first = game.state.snapshot()
    mm, ab = game.last_pair["Minimax"], game.last_pair["Alpha-Beta"]
    assert (mm.move, mm.value) == (ab.move, ab.value)
    assert game.pruning_ratio() == 1 - ab.nodes_expanded / mm.nodes_expanded
    assert game.comparison["Minimax"]["time"] == mm.elapsed
    game.reset()
    assert game.state.snapshot() == initial
    assert game.pruning_ratio() is None and game.log == []
    game.step()
    assert game.state.snapshot() == first
    game.reset(regenerate=True)
    assert game.seed != 3
    assert game.state.plies == 0


@pytest.fixture
def window(monkeypatch):
    monkeypatch.setenv("SDL_VIDEODRIVER", "dummy")
    monkeypatch.setenv("SDL_AUDIODRIVER", "dummy")
    view = AdversarialGui(seed=2, out=lambda text: None)
    yield view
    pygame.quit()


def click(window, name):
    return window.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN,
                                                button=1, pos=window.buttons[name].center))


def test_gui_controls_step_run_pause_reset_and_switch_settings(window):
    click(window, "compare")
    click(window, "step")
    assert window.session.state.plies == 1 and window.session.last_pair
    click(window, "run")
    window.update(window.next_move_at)
    assert window.running and window.session.state.plies == 2
    click(window, "depth_a")  # settings cannot change in the middle of autoplay
    assert window.session.depths[0] == 4
    click(window, "run")
    before = window.session.state.snapshot()
    window.update(window.next_move_at + 1000)
    assert window.session.state.snapshot() == before
    click(window, "depth_a")
    assert window.session.depths[0] == 6 and window.session.state.plies == 0
    click(window, "algo_a")
    assert window.session.algorithms[0] is Minimax
    click(window, "eval_a")
    assert window.session.evaluations[0].startswith("E2")
    click(window, "mode")
    click(window, "algo_b")
    assert window.session.mode == "AI vs AI" and window.session.algorithms[1] is Minimax
    click(window, "step")
    click(window, "reset")
    assert window.session.seed == 2 and window.session.state.plies == 0
    click(window, "new")
    assert window.session.seed != 2
    window.draw()


def test_human_moves_use_keys_and_board_clicks_without_terminal_input(window):
    click(window, "mode")
    click(window, "mode")
    assert window.session.mode == "Human vs AI"
    click(window, "step")  # A moves
    assert window.session.is_human_turn()
    before = window.session.state.snapshot()
    click(window, "step")  # B must supply a move
    assert window.session.state.snapshot() == before
    legal = window.session.state.legal_moves()[0]
    r, c = window.session.state.pos[1]
    keys = {(1, 0): pygame.K_DOWN, (-1, 0): pygame.K_UP,
            (0, 1): pygame.K_RIGHT, (0, -1): pygame.K_LEFT}
    key = keys[(legal[0] - r, legal[1] - c)]
    window.handle_event(pygame.event.Event(pygame.KEYDOWN, key=key))
    assert window.session.state.pos[1] == legal and window.session.state.plies == 2
    click(window, "step")
    legal = window.session.state.legal_moves()[0]
    window.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1,
                                         pos=window._cell_rect(legal).center))
    assert window.session.state.pos[1] == legal and window.session.state.plies == 4


def test_invalid_human_move_does_not_change_state(window):
    window.session.mode = "Human vs AI"
    window.session.reset()
    window.session.step()
    before = window.session.state.snapshot()
    assert not window.session.step((99, 99))
    assert window.session.state.snapshot() == before


def test_forced_pass_and_end_of_game_stop_autoplay(window):
    game = window.session
    game.mode = "Human vs AI"
    game.reset()
    game.state = make_state("A.T", "###", "B##", max_plies=4)
    game.paths = [[pos] for pos in game.state.pos]
    game.step()
    assert game.is_human_turn() and game.state.legal_moves() == [None]
    assert game.step() and game.state.plies == 2
    window.running = True
    window.update(window.next_move_at)
    assert game.state.is_terminal() and not window.running
    assert "A wins" in game.status()
    assert not window._enabled("run") and not window._enabled("step")


def test_back_and_quit_are_distinct_and_search_view_is_restored(window):
    assert click(window, "back") == "back"
    assert window.handle_event(pygame.event.Event(pygame.QUIT)) == "quit"
    grid = [[""] * 10 for _ in range(10)]
    parent = Gui(grid, lambda: grid, on_adversarial=lambda: True)
    parent.show_info(3, 5, 0.001)
    parent.solution_paths = [[(0, 0), (0, 1)]]
    pygame.display.set_mode((1000, 780))
    assert parent.open_adversarial()
    assert parent.screen.get_size() == parent.get_screen_size()
    assert parent.info == (3, 5, 0.001, None)
    assert parent.solution_paths == [[(0, 0), (0, 1)]]
    parent.on_adversarial = lambda: False
    assert not parent.open_adversarial()


def test_render_comparison_and_human_views(window, tmp_path):
    click(window, "compare")
    for _ in range(8):
        click(window, "step")
    window.draw()
    comparison = tmp_path / "comparison.png"
    pygame.image.save(window.screen, str(comparison))
    click(window, "mode")
    click(window, "mode")
    click(window, "step")
    window.draw()
    human = tmp_path / "human.png"
    pygame.image.save(window.screen, str(human))
    print(f"GUI previews: {comparison} | {human}")


@pytest.mark.parametrize("skip_input", ["button", "board", "enter", "key"])
def test_skipping_finishes_the_same_game_with_the_same_search_metrics(window, skip_input):
    expected = GameSession(2, out=lambda text: None)
    expected.compare = True
    while not expected.state.is_terminal():
        expected.step()
    click(window, "compare")
    click(window, "run")
    if skip_input == "button":
        click(window, "step")
    elif skip_input == "board":
        window.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1,
                                             pos=window._cell_rect((0, 0)).center))
    else:
        key = pygame.K_RETURN if skip_input == "enter" else pygame.K_a
        window.handle_event(pygame.event.Event(pygame.KEYDOWN, key=key))
    assert window.skip_animation
    for _ in range(200):
        window.update(0)  # skipping does not wait for animation timers
        if not window.running:
            break
    assert window.session.result() == expected.result()
    assert window.session.pruning_ratio() == expected.pruning_ratio()
    assert window.session.players[0].nodes_expanded == expected.players[0].nodes_expanded
    click(window, "reset")
    assert not window.skip_animation and not window.running


def test_normal_animation_waits_between_turns_and_pause_cancels_skip(window):
    click(window, "run")
    now = window.next_move_at
    window.update(now)
    assert window.session.state.plies == 1
    window.update(now + MOVE_DELAY - 1)
    assert window.session.state.plies == 1
    window.update(now + MOVE_DELAY)
    assert window.session.state.plies == 2
    click(window, "step")
    click(window, "run")
    assert not window.skip_animation and not window.running
    window.update(now + 1000)
    assert window.session.state.plies == 2


def test_skip_waits_for_human_input_and_keeps_processing_controls(window):
    click(window, "mode")
    click(window, "mode")
    click(window, "run")
    click(window, "step")
    window.update(0)
    assert window.session.is_human_turn() and window.session.state.plies == 1
    window.update(0)
    assert window.session.state.plies == 1
    move = window.session.state.legal_moves()[0]
    window.handle_event(pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1,
                                         pos=window._cell_rect(move).center))
    window.update(0)
    assert window.session.state.plies == 3 and window.session.is_human_turn()
    assert window.handle_event(pygame.event.Event(pygame.QUIT)) == "quit"
    click(window, "new")
    assert not window.running and not window.skip_animation
