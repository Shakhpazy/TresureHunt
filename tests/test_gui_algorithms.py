import runpy
from pathlib import Path

import pygame

from gui import ALGORITHMS, Gui
from adversarial.gui import AdversarialGui


def test_main_window_runs_every_algorithm_on_random_and_custom_grids(monkeypatch):
    # Use the real callbacks and drawing code without opening a desktop window.
    monkeypatch.setenv("SDL_VIDEODRIVER", "dummy")
    monkeypatch.setenv("SDL_AUDIODRIVER", "dummy")
    monkeypatch.setattr(Gui, "run", lambda self: None)
    monkeypatch.setattr(pygame.mouse, "set_cursor", lambda *args: None)
    monkeypatch.setattr(Gui, "_animation_interrupted", lambda self: True)
    app = runpy.run_path(str(Path(__file__).resolve().parents[1] / "main.py"))
    window = app["gui"]
    try:
        for custom_index in (None, 0, 1):
            if custom_index is not None:
                window._select_custom_grid(custom_index)
            for index, name in enumerate(ALGORITHMS):
                window._select_algorithm(index)
                window.run_algorithm()
                assert not window.busy
                assert window.info is not None, name
                if window.solution_paths:
                    assert all(window.grid[path[-1][0]][path[-1][1]] == "T"
                               for path in window.solution_paths)
                    if name in ("DFS", "BFS", "GBFS"):
                        assert window.info[0] == sum(len(path) - 1 for path in window.solution_paths)
                window.reset_overlay()
                assert window.info is None and window.solution_paths == []
        window.regenerate_grid()
        assert len(window.grid) == 20
        assert window.current_custom_grid_idx is None
        assert window.info is None
        previous_grid = window.grid

        def play_and_return(view):
            view.session.step()
            view.draw()
            return True

        monkeypatch.setattr(AdversarialGui, "run", play_and_return)
        assert window.open_adversarial()  # main.py's actual callback opens the new view
        assert window.grid is previous_grid
        assert window.screen.get_size() == window.get_screen_size()
    finally:
        pygame.quit()
