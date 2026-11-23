"""Play the two-agent Treasure Hunt in the terminal.

    python -m adversarial.play --mode ai-vs-random --seed 3 --depth 4
    python -m adversarial.play --mode ai-vs-ai --depth 4 --eval e1 --eval-b e3
    python -m adversarial.play --mode human-vs-ai --depth 4

Board legend:  A, B = agents   T = treasure   X = trap (blocks like a wall)   # = wall
"""
import argparse
import random
import sys

from adversarial.display import format_move, format_scoreboard, render
from adversarial.evaluation import EVALUATIONS
from adversarial.game import play_game
from adversarial.generator import generate_map
from adversarial.players import GameAborted, HumanPlayer, RandomPlayer, SearchPlayer
from adversarial.search import AlphaBeta, Minimax
from adversarial.state import A, B, MAX_PLIES, MAX_PLIES_LIMIT, GameState

ALGORITHMS = {"alphabeta": AlphaBeta, "minimax": Minimax}
EVAL_KEYS = {name.split()[0].lower(): (name, fn) for name, fn in EVALUATIONS.items()}  # e1, e2, e3
MAX_DEPTH = 10  # deeper than this is not useful here and would take minutes per move
MODES = ("ai-vs-random", "ai-vs-ai", "human-vs-ai")


def parse_args(argv=None):
    p = argparse.ArgumentParser(prog="python -m adversarial.play", description=__doc__.split("\n\n")[0])
    p.add_argument("--mode", choices=MODES, default="ai-vs-random")
    p.add_argument("--seed", type=int, default=None, help="map seed (default: a random one, which is printed)")
    p.add_argument("--algo", choices=ALGORITHMS, default="alphabeta", help="search used by the AI")
    p.add_argument("--depth", type=int, default=4, help=f"plies to look ahead, 1 to {MAX_DEPTH}")
    p.add_argument("--eval", choices=EVAL_KEYS, default="e1", dest="eval_key", help="evaluation used by the AI")
    p.add_argument("--algo-b", choices=ALGORITHMS, default=None, help="ai-vs-ai: search for B (default: same as A)")
    p.add_argument("--depth-b", type=int, default=None, help="ai-vs-ai: depth for B (default: same as A)")
    p.add_argument("--eval-b", choices=EVAL_KEYS, default=None, dest="eval_key_b", help="ai-vs-ai: evaluation for B")
    p.add_argument("--human-side", choices=("A", "B"), default="A", help="human-vs-ai: A moves first")
    p.add_argument("--max-plies", type=int, default=MAX_PLIES, help=f"turn cap, 1 to {MAX_PLIES_LIMIT}")
    p.add_argument("--board-every", type=int, default=1, help="draw the board every N plies (0 = only at the end)")
    p.add_argument("--no-color", action="store_true", help="never use colours")
    p.add_argument("--no-prompt", action="store_true", help="do not offer another game afterwards")
    args = p.parse_args(argv)

    for name in ("depth", "depth_b"):
        value = getattr(args, name)
        if value is not None and not 1 <= value <= MAX_DEPTH:
            p.error(f"--{name.replace('_', '-')} must be between 1 and {MAX_DEPTH}, got {value}")
    if not 1 <= args.max_plies <= MAX_PLIES_LIMIT:
        p.error(f"--max-plies must be between 1 and {MAX_PLIES_LIMIT}, got {args.max_plies}")
    if args.board_every < 0:
        p.error("--board-every cannot be negative")
    return args


def make_ai(algo_key, depth, eval_key):
    eval_name, evaluate = EVAL_KEYS[eval_key]
    return SearchPlayer(ALGORITHMS[algo_key], evaluate, depth, eval_name.split()[0])


def build_players(args, seed, input_fn, out):
    """(player_a, player_b) for the chosen mode. A moves first."""
    ai = make_ai(args.algo, args.depth, args.eval_key)
    if args.mode == "ai-vs-random":
        return ai, RandomPlayer(seed)
    if args.mode == "ai-vs-ai":
        second = make_ai(
            args.algo_b or args.algo,
            args.depth_b or args.depth,
            args.eval_key_b or args.eval_key,
        )
        return ai, second
    human = HumanPlayer(input_fn, out)
    return (human, ai) if args.human_side == "A" else (ai, human)


def run_session(args, seed, input_fn, out, color):
    """Play one game on the map for `seed`. Returns the GameResult, or None if it was aborted."""
    state = GameState(generate_map(seed), max_plies=args.max_plies)
    players = build_players(args, seed, input_fn, out)

    out(f"\nMap seed {seed}  |  A: {players[A].label}  |  B: {players[B].label}")
    out(f"{len(state.treasures)} treasures, {len(state.traps)} traps; A moves first.\n")
    out(render(state, color))
    out(format_scoreboard(state) + "\n")

    def on_move(state, who, before, move, took, player):
        out(format_move(state.plies, who, player.label, before, move, took, player.last_info()))
        if args.board_every and state.plies % args.board_every == 0 and not state.is_terminal():
            out("\n" + render(state, color))
            out(format_scoreboard(state) + "\n")

    try:
        result = play_game(state, players, on_move)
    except GameAborted:
        out("\nGame aborted.")
        return None

    out("\nFinal board:\n" + render(state, color))
    out(format_scoreboard(state))
    out(summarise(result, players))
    return result


def summarise(result, players):
    if result.winner is None:
        verdict = "Draw."
    else:
        verdict = f"Winner: {'AB'[result.winner]} ({players[result.winner].label})."
    lines = [f"\n{verdict} Treasures A={result.scores[A]} B={result.scores[B]}, {result.plies} plies"
             + (" (ended by the ply cap)." if result.capped else ".")]
    for who in (A, B):
        player = players[who]
        if getattr(player, "searches", 0):
            lines.append(
                f"  {'AB'[who]} {player.label}: {player.searches} searches, "
                f"{player.nodes_expanded} nodes expanded, {player.elapsed:.3f}s total"
                + (f", {player.cutoffs} cutoffs" if player.cutoffs else "")
            )
        path = " -> ".join(f"({r},{c})" for r, c in result.paths[who])
        lines.append(f"  {'AB'[who]} path ({len(result.paths[who]) - 1} moves): {path}")
    return "\n".join(lines)


def ask_what_next(input_fn, out):
    """'n' new map, 's' same map again, anything else (or no input) quits."""
    try:
        answer = input_fn("\nPlay again? [n]ew map / [s]ame map / [q]uit: ").strip().lower()
    except EOFError:
        return "q"
    return answer if answer in ("n", "s") else "q"


def main(argv=None, input_fn=input, out=print, interactive=None):
    args = parse_args(argv)
    if interactive is None:
        interactive = sys.stdin.isatty()
    color = not args.no_color and sys.stdout.isatty()
    seed = args.seed if args.seed is not None else random.randrange(1_000_000)

    while True:
        try:
            result = run_session(args, seed, input_fn, out, color)
        except ValueError as error:  # the generator could not build a map for this seed
            out(f"Could not set up the game: {error}")
            return 2
        if result is None or not interactive or args.no_prompt:
            return 0
        choice = ask_what_next(input_fn, out)
        if choice == "q":
            return 0
        if choice == "n":  # regenerate: a brand new map
            seed = random.randrange(1_000_000)
        # "s": reset the game on the same map (same seed, fresh state and players)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\nGame aborted.")
        sys.exit(130)
