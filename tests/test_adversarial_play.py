import re

import pytest

from adversarial import play


def run(argv, answers=(), interactive=False):
    """Run the CLI with scripted input; returns (exit code, everything it printed, prompts seen)."""
    printed, prompts, queue = [], [], list(answers)

    def fake_input(prompt):
        prompts.append(prompt)
        if callable(queue[0] if queue else None):
            return queue[0](prompt)
        if not queue:
            raise EOFError
        return queue.pop(0)

    code = play.main(argv, input_fn=fake_input, out=printed.append, interactive=interactive)
    return code, "\n".join(printed), prompts


def without_timings(text):
    # the only run-to-run difference between two identical games is how long the CPU took
    return re.sub(r"time=[\d.]+ms|[\d.]+s total", "T", text)


def test_ai_vs_random_plays_a_whole_game_and_reports_the_result():
    code, text, _ = run(["--seed", "2", "--depth", "3", "--board-every", "0"])
    assert code == 0
    assert "Map seed 2" in text and "Final board" in text
    assert re.search(r"Winner: A|Winner: B|Draw\.", text)
    assert "nodes expanded" in text and "path (" in text


def test_same_seed_gives_the_same_game():
    argv = ["--seed", "7", "--depth", "3", "--board-every", "0"]
    assert without_timings(run(argv)[1]) == without_timings(run(argv)[1])


def test_ai_vs_ai_can_use_different_algorithms_depths_and_evaluations():
    code, text, _ = run(["--mode", "ai-vs-ai", "--seed", "3", "--depth", "2", "--eval", "e1",
                         "--algo-b", "minimax", "--depth-b", "3", "--eval-b", "e3", "--board-every", "0"])
    assert code == 0
    assert "A: Alpha-Beta d2 E1" in text and "B: Minimax d3 E3" in text


def test_human_vs_ai_plays_through_with_scripted_moves():
    def take_first_option(prompt):
        return re.search(r"\[(\w)", prompt).group(1)  # the first direction offered

    code, text, prompts = run(["--mode", "human-vs-ai", "--seed", "4", "--depth", "2",
                               "--max-plies", "20", "--board-every", "0"], answers=[take_first_option] * 1)
    assert code == 0
    assert "A: human" in text and "ended by the ply cap" in text
    assert len(prompts) == 10  # the human moved on 10 of the 20 plies


def test_human_can_quit_mid_game():
    code, text, _ = run(["--mode", "human-vs-ai", "--seed", "4", "--depth", "2"], answers=["q"])
    assert code == 0 and "Game aborted" in text and "Final board" not in text


def test_human_can_play_second_as_b():
    code, text, prompts = run(["--mode", "human-vs-ai", "--human-side", "B", "--seed", "4", "--depth", "2",
                               "--max-plies", "10", "--board-every", "0"],
                              answers=[lambda prompt: re.search(r"\[(\w)", prompt).group(1)])
    assert "B: human" in text and "A: Alpha-Beta" in text and len(prompts) == 5


def test_play_again_same_map_resets_and_new_map_regenerates():
    base = ["--seed", "5", "--depth", "2", "--max-plies", "10", "--board-every", "0"]
    code, text, _ = run(base, answers=["s", "q"], interactive=True)
    assert code == 0 and text.count("Map seed 5") == 2  # reset: same map again

    code, text, _ = run(base, answers=["n", "q"], interactive=True)
    seeds = re.findall(r"Map seed (\d+)", text)
    assert len(seeds) == 2 and seeds[0] == "5" and seeds[1] != "5"  # regenerate: a different map


def test_play_again_prompt_is_skipped_when_not_interactive_or_when_asked():
    _, _, prompts = run(["--seed", "5", "--depth", "2"], interactive=False)
    assert prompts == []
    _, _, prompts = run(["--seed", "5", "--depth", "2", "--no-prompt"], interactive=True)
    assert prompts == []


def test_closed_input_at_the_play_again_prompt_just_stops():
    code, _, prompts = run(["--seed", "5", "--depth", "2"], interactive=True)  # no answers: EOF
    assert code == 0 and len(prompts) == 1


@pytest.mark.parametrize("argv", [
    ["--depth", "0"], ["--depth", "11"], ["--depth", "x"], ["--depth-b", "99"],
    ["--max-plies", "0"], ["--max-plies", "401"], ["--board-every", "-1"],
    ["--mode", "nonsense"], ["--eval", "e9"], ["--algo", "dfs"],
])
def test_bad_arguments_are_rejected_with_a_usage_error(argv):
    with pytest.raises(SystemExit) as exit_info:
        play.parse_args(argv)
    assert exit_info.value.code == 2


def test_a_map_that_cannot_be_generated_gives_a_clear_message_not_a_crash(monkeypatch):
    def impossible(seed):
        raise ValueError("no layout with every treasure reachable")

    monkeypatch.setattr(play, "generate_map", impossible)
    code, text, _ = run(["--seed", "1"])
    assert code == 2 and "Could not set up the game" in text
