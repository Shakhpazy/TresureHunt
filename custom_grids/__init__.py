"""Load the hand-made grids stored next to this file."""

import json
from pathlib import Path

from grid import EMPTY, START, STATIC_WALLS, TRAP, TREASURE


CELL_SYMBOLS = {".": EMPTY, "S": START, "#": STATIC_WALLS, "X": TRAP, "T": TREASURE}


def load_custom_grids():
    grids = []
    for path in sorted(Path(__file__).parent.glob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        rows = data["grid"]
        if len(rows) != 10 or any(len(row) != 10 for row in rows):
            raise ValueError(f"{path.name} must contain a 10x10 grid")
        if any(symbol not in CELL_SYMBOLS for row in rows for symbol in row):
            raise ValueError(f"{path.name} contains an unknown grid symbol")

        grid = [[CELL_SYMBOLS[symbol] for symbol in row] for row in rows]
        if sum(cell == START for row in grid for cell in row) != 1:
            raise ValueError(f"{path.name} must contain exactly one start (S)")
        grids.append((data.get("name", path.stem), grid))
    return grids
