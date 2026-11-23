"""Seeded map generator for the two-agent game.

Why a new generator instead of reusing grid.TreasureMap: TreasureMap hardcodes the item
counts, places only one start, draws from the global `random` (so it cannot be seeded
without side effects) and never checks that the treasures can be reached. This module
reuses the cell constants from grid.py, so the symbols stay identical across the project.
"""
import random
from collections import deque, namedtuple

from grid import EMPTY, STATIC_WALLS, TRAP, TREASURE

GRID_SIZE = 15
WALL_RATIO = 0.15
TREASURE_COUNTS = (3, 5)  # always odd, so a finished game can never end tied on treasures
TRAP_COUNTS = (2, 3)      # inclusive range
MAX_ATTEMPTS = 1000

# grid holds only the static things (walls, traps, treasures). The two agents are NOT in
# the grid: their positions change every turn, so the game state tracks them separately.
GameMap = namedtuple("GameMap", ["grid", "start_a", "start_b", "seed"])

_DIRECTIONS = ((1, 0), (0, 1), (-1, 0), (0, -1))


def generate_map(seed, size=GRID_SIZE, treasures=None, traps=None, walls=None):
    """Return a GameMap that is identical every time it is called with the same arguments.

    treasures: 3 or 5 (None picks one from the seed). traps: 2 to 3 (None picks one from
    the seed). walls: defaults to 15 % of the cells.
    Raises ValueError for impossible requests, or if no layout where both agents can reach
    every treasure is found within MAX_ATTEMPTS tries.
    """
    # a private generator: seeding it never disturbs the global `random` module
    rng = random.Random(seed)

    if treasures is None:
        treasures = rng.choice(TREASURE_COUNTS)
    elif treasures not in TREASURE_COUNTS:
        raise ValueError(f"treasures must be one of {TREASURE_COUNTS}, got {treasures}")

    if traps is None:
        traps = rng.randint(*TRAP_COUNTS)
    elif not TRAP_COUNTS[0] <= traps <= TRAP_COUNTS[1]:
        raise ValueError(f"traps must be between {TRAP_COUNTS[0]} and {TRAP_COUNTS[1]}, got {traps}")

    if size < 2:
        raise ValueError(f"size must be at least 2, got {size}")
    if walls is None:
        walls = round(size * size * WALL_RATIO)
    if walls < 1:
        raise ValueError(f"there must be at least one wall, got {walls}")

    needed = walls + traps + treasures + 2  # +2 for the two agents
    if needed > size * size:
        raise ValueError(f"{needed} items do not fit on a {size}x{size} grid")

    all_cells = [(r, c) for r in range(size) for c in range(size)]

    for _ in range(MAX_ATTEMPTS):
        # shuffle every cell once and deal them out: no cell can be picked twice, so there
        # is no "placed on an occupied cell, try again" loop like TreasureMap.placeItem has
        cells = all_cells[:]
        rng.shuffle(cells)
        cut = 0
        wall_cells = cells[cut:cut + walls]; cut += walls
        trap_cells = cells[cut:cut + traps]; cut += traps
        treasure_cells = cells[cut:cut + treasures]; cut += treasures
        start_a, start_b = cells[cut], cells[cut + 1]

        grid = [[EMPTY for _ in range(size)] for _ in range(size)]
        for r, c in wall_cells:
            grid[r][c] = STATIC_WALLS
        for r, c in trap_cells:
            grid[r][c] = TRAP
        for r, c in treasure_cells:
            grid[r][c] = TREASURE

        if _everything_reachable(grid, start_a, start_b, treasure_cells):
            return GameMap(grid, start_a, start_b, seed)

    raise ValueError(
        f"no layout with every treasure reachable found in {MAX_ATTEMPTS} attempts "
        f"(size={size}, walls={walls}, traps={traps})"
    )


def _everything_reachable(grid, start_a, start_b, treasure_cells):
    """Flood fill from agent A through open cells (walls and traps are blocked).

    Agent B and every treasure must be inside the region A can reach. Because movement is
    reversible, "reachable from A" means the same region is reachable from B.
    """
    size = len(grid)
    seen = {start_a}
    queue = deque([start_a])
    while queue:
        r, c = queue.popleft()
        for dr, dc in _DIRECTIONS:
            nr, nc = r + dr, c + dc
            if (
                0 <= nr < size and 0 <= nc < size
                and (nr, nc) not in seen
                and grid[nr][nc] not in (STATIC_WALLS, TRAP)
            ):
                seen.add((nr, nc))
                queue.append((nr, nc))
    return start_b in seen and all(t in seen for t in treasure_cells)
