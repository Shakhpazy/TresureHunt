import random

import pytest

from adversarial import generator
from adversarial.generator import generate_map
from grid import STATIC_WALLS, TRAP, TREASURE


def count(grid, symbol):
    return sum(row.count(symbol) for row in grid)


def test_same_seed_gives_identical_map():
    first, second = generate_map(7), generate_map(7)
    assert first == second


def test_different_seeds_give_different_maps():
    assert generate_map(1).grid != generate_map(2).grid


def test_seeding_does_not_touch_the_global_random_module():
    random.seed(123)
    expected = random.random()
    random.seed(123)
    generate_map(5)
    assert random.random() == expected


def test_default_counts_follow_the_assignment():
    for seed in range(100):
        game_map = generate_map(seed)
        grid = game_map.grid
        assert len(grid) == 15 and all(len(row) == 15 for row in grid)
        assert count(grid, TREASURE) in (3, 5)
        assert 2 <= count(grid, TRAP) <= 3
        assert count(grid, STATIC_WALLS) == round(15 * 15 * generator.WALL_RATIO)


def test_both_treasure_counts_actually_occur():
    assert {count(generate_map(seed).grid, TREASURE) for seed in range(40)} == {3, 5}


def test_agents_start_on_distinct_open_cells():
    for seed in range(100):
        game_map = generate_map(seed)
        assert game_map.start_a != game_map.start_b
        for r, c in (game_map.start_a, game_map.start_b):
            assert game_map.grid[r][c] == ""


def test_every_treasure_and_the_other_agent_reachable_from_agent_a():
    for seed in range(200):
        game_map = generate_map(seed)
        treasures = [
            (r, c) for r, row in enumerate(game_map.grid) for c, cell in enumerate(row) if cell == TREASURE
        ]
        assert generator._everything_reachable(game_map.grid, game_map.start_a, game_map.start_b, treasures)


def test_reachability_check_catches_a_walled_off_treasure():
    # the treasure sits behind a wall column, so agent A cannot get to it
    grid = [["", "#", "T"], ["", "#", ""], ["", "#", ""]]
    assert not generator._everything_reachable(grid, (0, 0), (1, 0), [(0, 2)])
    # a trap blocks just like a wall
    grid = [["", "X", "T"], ["", "X", ""], ["", "X", ""]]
    assert not generator._everything_reachable(grid, (0, 0), (1, 0), [(0, 2)])


@pytest.mark.parametrize("kwargs", [
    {"treasures": 4},      # even: could tie
    {"treasures": 1},
    {"traps": 1},
    {"traps": 4},
    {"size": 1},
    {"walls": 0},
    {"size": 3},           # 15 % walls + items do not fit on 3x3 (needs 1+3+3+2)
])
def test_impossible_requests_raise_value_error(kwargs):
    with pytest.raises(ValueError):
        generate_map(0, **kwargs)


def test_gives_up_with_a_clear_error_when_no_layout_works(monkeypatch):
    monkeypatch.setattr(generator, "MAX_ATTEMPTS", 5)
    # a 4x4 grid packed with 11 walls leaves almost no room, so it is rarely connected
    with pytest.raises(ValueError, match="attempts"):
        generate_map(0, size=4, walls=7, treasures=5, traps=2)
