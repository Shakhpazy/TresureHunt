"""Experiments for the report.

    python -m adversarial.experiments table          # Minimax vs Alpha-Beta, one game each (README table)
    python -m adversarial.experiments pruning        # Minimax vs Alpha-Beta: nodes, time, pruning
    python -m adversarial.experiments h2h            # E1 vs E2 vs E3, head to head
    python -m adversarial.experiments all

pruning: for each map, evaluation and depth, agent A plays a whole game against a random B. At
every one of A's turns BOTH Minimax and Alpha-Beta search the SAME position, so the node counts
and times compare like with like. The two must pick the same move (and value); if they ever
disagree the script stops, because that would mean the pruning is wrong.

h2h: two evaluation functions play each other with the same search and depth. Every pairing is
played from both sides on every map, so the advantage of moving first cancels out.
"""
import argparse
import itertools
import time

from adversarial.evaluation import EVALUATIONS
from adversarial.game import play_game
from adversarial.generator import generate_map
from adversarial.players import RandomPlayer, SearchPlayer
from adversarial.search import AlphaBeta, Minimax
from adversarial.state import A, B, GameState


def pruning_study(seeds, depths, evaluations=None):
    """One result dict per (seed, evaluation, depth). See the module docstring."""
    evaluations = evaluations or EVALUATIONS
    rows = []
    for seed in seeds:
        for eval_name, evaluate in evaluations.items():
            for depth in depths:
                rows.append(_pruning_game(seed, eval_name, evaluate, depth))
    return rows


def _pruning_game(seed, eval_name, evaluate, depth):
    state = GameState(generate_map(seed))
    opponent = RandomPlayer(seed)
    minimax, alphabeta = Minimax(evaluate, depth), AlphaBeta(evaluate, depth)
    totals = dict(positions=0, mm_nodes=0, ab_nodes=0, mm_time=0.0, ab_time=0.0, cutoffs=0)

    while not state.is_terminal():
        if state.turn == A:
            plain = minimax.search(state)
            pruned = alphabeta.search(state)
            if (plain.value, plain.move) != (pruned.value, pruned.move):
                raise AssertionError(
                    f"Alpha-Beta disagreed with Minimax (seed {seed}, {eval_name}, depth {depth}, "
                    f"ply {state.plies}): {pruned.move}/{pruned.value} vs {plain.move}/{plain.value}"
                )
            totals["positions"] += 1
            totals["mm_nodes"] += plain.nodes_expanded
            totals["ab_nodes"] += pruned.nodes_expanded
            totals["mm_time"] += plain.elapsed
            totals["ab_time"] += pruned.elapsed
            totals["cutoffs"] += pruned.cutoffs
            state.play(pruned.move)
        else:
            state.play(opponent.choose(state))

    totals.update(seed=seed, evaluation=eval_name, depth=depth, plies=state.plies)
    # observed pruning ratio: the share of Minimax's nodes that Alpha-Beta did not have to visit
    totals["pruning_ratio"] = 1 - totals["ab_nodes"] / totals["mm_nodes"]
    return totals


def comparison_table(seeds, depths, eval_name="E1 baseline", repeats=3):
    """One full game per (map, depth, algorithm): agent A (using that search) against a random B.

    Nodes are the total over all of A's searches in the game. Time is the total search time,
    the median of `repeats` identical runs, because one run of a millisecond-scale search is
    noisy. Minimax and Alpha-Beta choose identical moves, so they play identical games and
    differ only in work done.
    """
    evaluate = EVALUATIONS[eval_name]
    rows = []
    for seed in seeds:
        for depth in depths:
            for algorithm in (Minimax, AlphaBeta):
                times, nodes_seen = [], set()
                for _ in range(repeats):
                    player = SearchPlayer(algorithm, evaluate, depth, eval_name)
                    result = play_game(GameState(generate_map(seed)), (player, RandomPlayer(seed)))
                    times.append(player.elapsed)
                    nodes_seen.add(player.nodes_expanded)
                if len(nodes_seen) != 1:  # the search is deterministic, so this can never differ
                    raise AssertionError(f"node count changed between identical runs: {nodes_seen}")
                rows.append(dict(
                    seed=seed, algorithm=algorithm.name, depth=depth, nodes=nodes_seen.pop(),
                    time=sorted(times)[len(times) // 2], plies=result.plies, scores=result.scores,
                    outcome="Win" if result.winner == A else "Loss" if result.winner == B else "Draw",
                ))
    return rows


def head_to_head(seeds, depths, algorithm=AlphaBeta, evaluations=None):
    """One result dict per (pairing, depth). Pairings: every two different evaluations, plus a
    mirror match of the first evaluation against itself as a control for the side advantage."""
    evaluations = evaluations or EVALUATIONS
    names = list(evaluations)
    pairings = list(itertools.combinations(names, 2)) + [(names[0], names[0])]
    results = []
    for first, second in pairings:
        for depth in depths:
            results.append(_pairing(first, second, seeds, depth, algorithm, evaluations))
    return results


def _pairing(first, second, seeds, depth, algorithm, evaluations):
    row = dict(first=first, second=second, depth=depth, games=0, first_wins=0, second_wins=0,
               draws=0, mover_wins=0, capped=0, plies=0, first_treasures=0, second_treasures=0)
    for seed in seeds:
        # a mirror match is the same game from either side, so play it once
        sides = [(first, second)] if first == second else [(first, second), (second, first)]
        for name_a, name_b in sides:
            players = (
                SearchPlayer(algorithm, evaluations[name_a], depth, name_a),
                SearchPlayer(algorithm, evaluations[name_b], depth, name_b),
            )
            result = play_game(GameState(generate_map(seed)), players)
            winner_name = None if result.winner is None else (name_a, name_b)[result.winner]
            row["games"] += 1
            row["plies"] += result.plies
            row["capped"] += result.capped
            row["mover_wins"] += result.winner == A
            if winner_name is None:
                row["draws"] += 1
            elif winner_name == first and first != second:
                row["first_wins"] += 1
            elif winner_name == second and first != second:
                row["second_wins"] += 1
            # treasures credited to each evaluation, wherever it sat
            mine, theirs = (result.scores[A], result.scores[B]) if name_a == first else (result.scores[B], result.scores[A])
            row["first_treasures"] += mine
            row["second_treasures"] += theirs
    return row


# ---- printing ------------------------------------------------------------------------------

def format_table(headers, rows):
    """A Markdown table, which also reads fine as plain text in the terminal."""
    widths = [max(len(str(h)), *(len(str(r[i])) for r in rows)) for i, h in enumerate(headers)]
    def line(cells):
        return "| " + " | ".join(str(c).ljust(w) for c, w in zip(cells, widths)) + " |"
    return "\n".join([line(headers), "|" + "|".join("-" * (w + 2) for w in widths) + "|"]
                     + [line(r) for r in rows])


def print_pruning(rows, out=print):
    out("## Minimax vs Alpha-Beta (same positions, same move chosen every time)\n")
    table = []
    for r in rows:
        table.append([
            r["seed"], r["evaluation"], r["depth"], r["positions"],
            f"{r['mm_nodes'] / r['positions']:.0f}", f"{r['ab_nodes'] / r['positions']:.0f}",
            f"{r['pruning_ratio'] * 100:.1f}%",
            f"{r['mm_time'] / r['positions'] * 1000:.3f}", f"{r['ab_time'] / r['positions'] * 1000:.3f}",
        ])
    out(format_table(["map seed", "evaluation", "depth", "moves", "Minimax nodes/move",
                      "Alpha-Beta nodes/move", "pruned", "Minimax ms/move", "Alpha-Beta ms/move"], table))

    out("\n### Summary by depth (all maps and evaluations together)\n")
    summary = []
    for depth in sorted({r["depth"] for r in rows}):
        group = [r for r in rows if r["depth"] == depth]
        positions = sum(r["positions"] for r in group)
        mm, ab = sum(r["mm_nodes"] for r in group), sum(r["ab_nodes"] for r in group)
        mm_t, ab_t = sum(r["mm_time"] for r in group), sum(r["ab_time"] for r in group)
        summary.append([depth, positions, f"{mm / positions:.0f}", f"{ab / positions:.0f}",
                        f"{(1 - ab / mm) * 100:.1f}%", f"{mm_t / positions * 1000:.3f}",
                        f"{ab_t / positions * 1000:.3f}", f"{mm_t / ab_t:.1f}x"])
    out(format_table(["depth", "moves", "Minimax nodes/move", "Alpha-Beta nodes/move", "pruned",
                      "Minimax ms/move", "Alpha-Beta ms/move", "time ratio"], summary))


def print_comparison(rows, out=print):
    out("## Minimax vs Alpha-Beta: one full game each (agent A against a random B)\n")
    out(format_table(
        ["Map", "Algorithm", "Depth", "Nodes Expanded", "Execution Time(s)", "Outcome"],
        [[r["seed"], r["algorithm"], r["depth"], r["nodes"], f"{r['time']:.4f}", r["outcome"]] for r in rows],
    ))
    out("\n### Totals over all maps\n")
    summary = []
    for depth in sorted({r["depth"] for r in rows}):
        for name in ("Minimax", "Alpha-Beta"):
            group = [r for r in rows if r["depth"] == depth and r["algorithm"] == name]
            summary.append([
                name, depth, sum(r["nodes"] for r in group), f"{sum(r['time'] for r in group):.4f}",
                f"{sum(r['outcome'] == 'Win' for r in group)}W "
                f"{sum(r['outcome'] == 'Draw' for r in group)}D {sum(r['outcome'] == 'Loss' for r in group)}L",
            ])
    out(format_table(["Algorithm", "Depth", "Nodes Expanded", "Execution Time(s)", "Outcomes"], summary))


def print_head_to_head(results, out=print):
    out("## Evaluation functions head to head (each pairing played from both sides on every map)\n")
    table = []
    for r in results:
        mirror = r["first"] == r["second"]
        table.append([
            f"{r['first']} vs {r['second']}" + (" (control)" if mirror else ""), r["depth"], r["games"],
            "-" if mirror else r["first_wins"], "-" if mirror else r["second_wins"], r["draws"],
            f"{r['mover_wins']}/{r['games']}", r["capped"], f"{r['plies'] / r['games']:.0f}",
            f"{r['first_treasures']}-{r['second_treasures']}",
        ])
    out(format_table(["pairing", "depth", "games", "left wins", "right wins", "draws",
                      "first mover won", "hit ply cap", "avg plies", "treasures (left-right)"], table))


def parse_args(argv=None):
    p = argparse.ArgumentParser(prog="python -m adversarial.experiments", description=__doc__.split("\n\n")[0])
    p.add_argument("which", choices=("table", "pruning", "h2h", "all"))
    p.add_argument("--depths", type=_int_list, default=[2, 4, 6], help="comma separated, default 2,4,6")
    p.add_argument("--pruning-seeds", type=_int_list, default=[1, 2, 3], help="maps for the pruning study")
    p.add_argument("--maps", type=int, default=10, help="number of maps (seeds 1..N) for head to head")
    args = p.parse_args(argv)
    if any(d < 1 or d > 10 for d in args.depths):
        p.error("every depth must be between 1 and 10")
    if args.maps < 1:
        p.error("--maps must be at least 1")
    return args


def _int_list(text):
    try:
        return [int(part) for part in text.split(",") if part.strip()]
    except ValueError:
        raise argparse.ArgumentTypeError(f"expected comma separated whole numbers, got {text!r}") from None


def main(argv=None, out=print):
    args = parse_args(argv)
    started = time.perf_counter()
    if args.which in ("table", "all"):
        print_comparison(comparison_table(args.pruning_seeds, args.depths), out)
    if args.which in ("pruning", "all"):
        if args.which == "all":
            out("")
        print_pruning(pruning_study(args.pruning_seeds, args.depths), out)
    if args.which in ("h2h", "all"):
        if args.which == "all":
            out("")
        print_head_to_head(head_to_head(range(1, args.maps + 1), args.depths), out)
    out(f"\n(finished in {time.perf_counter() - started:.1f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
