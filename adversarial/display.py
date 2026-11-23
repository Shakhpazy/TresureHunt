"""Turning a GameState into text for the terminal."""
from grid import STATIC_WALLS

# every kind of cell has its own letter, so the board is readable even without colour
WALL, TRAP_GLYPH, TREASURE_GLYPH, EMPTY_GLYPH = "#", "X", "T", "."
AGENT_GLYPHS = ("A", "B")

_COLORS = {
    WALL: "\033[94m",            # blue
    TRAP_GLYPH: "\033[91m",      # red
    TREASURE_GLYPH: "\033[93m",  # yellow
    "A": "\033[92m",             # green
    "B": "\033[95m",             # magenta
}
_RESET = "\033[0m"


def render(state, color=False):
    """The board as a string, with row and column numbers so logged (row, col) can be found."""
    # every cell is 3 characters wide ("  X"), and the row label is 3 wide ("12 "),
    # so each column number in the header sits right above its glyphs
    lines = ["   " + "".join(f"{c:>3}" for c in range(state.cols))]
    for r in range(state.rows):
        cells = []
        for c in range(state.cols):
            glyph = _glyph_at(state, (r, c))
            if color and glyph in _COLORS:
                glyph = f"{_COLORS[glyph]}{glyph}{_RESET}"
            cells.append(f"  {glyph}")
        lines.append(f"{r:>2} " + "".join(cells))
    return "\n".join(lines)


def _glyph_at(state, cell):
    # agents are drawn on top of everything: they can only stand on open cells anyway
    for index, glyph in enumerate(AGENT_GLYPHS):
        if state.pos[index] == cell:
            return glyph
    if cell in state.treasures:
        return TREASURE_GLYPH
    if cell in state.traps:
        return TRAP_GLYPH
    if state.grid[cell[0]][cell[1]] == STATIC_WALLS:
        return WALL
    return EMPTY_GLYPH  # includes cells whose treasure has already been collected


def format_scoreboard(state):
    return (
        f"score  A={state.scores[0]}  B={state.scores[1]}   "
        f"treasures left={len(state.treasures)}   ply={state.plies}/{state.max_plies}"
    )


def format_move(ply, who, label, before, move, took_treasure, info=""):
    """One log line for a move, for example:
    ply  12 | A (Alpha-Beta d4 E1) (3, 4) -> (3, 5) +treasure | value=98 nodes=420 ...
    """
    who_text = f"{AGENT_GLYPHS[who]} ({label})"
    if move is None:
        action = "passes (no legal move)"
    else:
        action = f"{before} -> {move}" + (" +treasure" if took_treasure else "")
    line = f"ply {ply:>3} | {who_text} {action}"
    return f"{line} | {info}" if info else line
