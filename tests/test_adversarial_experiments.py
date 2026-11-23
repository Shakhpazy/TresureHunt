import pytest

from adversarial import experiments
from adversarial.evaluation import EVALUATIONS
from adversarial.search import AlphaBeta


def test_pruning_study_reports_consistent_numbers():
    rows = experiments.pruning_study(seeds=[1, 2], depths=[2, 4])
    assert len(rows) == 2 * len(EVALUATIONS) * 2
    for row in rows:
        assert row["positions"] > 0
        assert row["ab_nodes"] <= row["mm_nodes"]
        assert 0 <= row["pruning_ratio"] < 1
        assert row["pruning_ratio"] == pytest.approx(1 - row["ab_nodes"] / row["mm_nodes"])
        assert row["cutoffs"] > 0 or row["depth"] == 1


def test_pruning_grows_with_depth_on_average():
    rows = experiments.pruning_study(seeds=[1, 2, 3], depths=[2, 6])
    def ratio(depth):
        group = [r for r in rows if r["depth"] == depth]
        return 1 - sum(r["ab_nodes"] for r in group) / sum(r["mm_nodes"] for r in group)
    assert ratio(6) > ratio(2)


def test_the_study_stops_loudly_if_alpha_beta_ever_disagrees_with_minimax(monkeypatch):
    class BrokenAlphaBeta(AlphaBeta):
        def _value(self, state, depth, alpha, beta):
            return super()._value(state, depth, alpha, beta) + (1 if depth == 0 else 0)  # skews leaves

    monkeypatch.setattr(experiments, "AlphaBeta", BrokenAlphaBeta)
    with pytest.raises(AssertionError, match="disagreed with Minimax"):
        experiments.pruning_study(seeds=[1], depths=[3])


def test_comparison_table_has_one_row_per_game_and_both_algorithms_play_the_same_game():
    rows = experiments.comparison_table(seeds=[1, 2], depths=[2, 4], repeats=2)
    assert len(rows) == 2 * 2 * 2
    for seed in (1, 2):
        for depth in (2, 4):
            mm = next(r for r in rows if (r["seed"], r["depth"], r["algorithm"]) == (seed, depth, "Minimax"))
            ab = next(r for r in rows if (r["seed"], r["depth"], r["algorithm"]) == (seed, depth, "Alpha-Beta"))
            # same moves chosen, so the same game: only the work differs
            assert (mm["outcome"], mm["plies"], mm["scores"]) == (ab["outcome"], ab["plies"], ab["scores"])
            assert 0 < ab["nodes"] <= mm["nodes"]
            assert mm["time"] > 0 and ab["time"] > 0
            assert mm["outcome"] in ("Win", "Loss", "Draw")


def test_comparison_table_prints_the_assignment_columns():
    out = []
    experiments.print_comparison(experiments.comparison_table([1], [2], repeats=1), out.append)
    text = "\n".join(out)
    header_line = next(line for line in text.split("\n") if line.startswith("| Map"))
    columns = [cell.strip() for cell in header_line.strip("|").split("|")]
    assert columns == ["Map", "Algorithm", "Depth", "Nodes Expanded", "Execution Time(s)", "Outcome"]
    assert "Totals over all maps" in text


def test_head_to_head_counts_add_up():
    results = experiments.head_to_head(seeds=[1, 2, 3], depths=[2])
    assert len(results) == 3 + 1  # three pairings plus the mirror control
    for row in results:
        decisive = row["first_wins"] + row["second_wins"]
        if row["first"] == row["second"]:
            assert row["games"] == 3                      # a mirror match is played once per map
            assert decisive == 0
        else:
            assert row["games"] == 6                      # both sides on every map
            assert decisive + row["draws"] == row["games"]
        assert 0 <= row["capped"] <= row["games"]
        assert 0 <= row["mover_wins"] <= row["games"]


def test_head_to_head_is_deterministic():
    first = experiments.head_to_head(seeds=[1, 2], depths=[2])
    second = experiments.head_to_head(seeds=[1, 2], depths=[2])
    assert first == second


def test_a_strong_evaluation_beats_a_useless_one_both_ways_round():
    evaluations = {"smart": EVALUATIONS["E1 baseline"], "blind": lambda state, me: 0}
    row = experiments._pairing("smart", "blind", seeds=[1, 2, 3, 4], depth=4,
                               algorithm=AlphaBeta, evaluations=evaluations)
    assert row["first_wins"] > row["second_wins"]  # the harness credits wins to the right side


def test_table_formatting_is_a_valid_markdown_table():
    text = experiments.format_table(["a", "bb"], [[1, "x"], [22, "yyy"]])
    lines = text.split("\n")
    assert len(lines) == 4 and lines[1].replace("|", "").replace("-", "") == ""
    assert len({len(line) for line in lines}) == 1  # every row is the same width


def test_command_line_runs_and_rejects_bad_arguments():
    out = []
    assert experiments.main(["pruning", "--pruning-seeds", "1", "--depths", "2"], out=out.append) == 0
    assert any("Summary by depth" in chunk for chunk in out)
    for argv in (["pruning", "--depths", "0"], ["h2h", "--maps", "0"], ["pruning", "--depths", "a,b"], ["nothing"]):
        with pytest.raises(SystemExit) as exit_info:
            experiments.parse_args(argv)
        assert exit_info.value.code == 2
