"""Open the normal Treasure Hunt window on one hand-made grid.

Edit the settings below, then run:  python custom_grid.py
Pick an algorithm and click Run exactly like main.py. The layout never changes.
"Regenerate Grid" keeps the same layout, it only re-rolls the random UCS weights.
"""
from grid import EMPTY, START, STATIC_WALLS, TRAP, TREASURE, create_weight_matrix

# ---- settings you edit ------------------------------------------------------
GRID_SIZE = 10
# START_POS = (0, 0)       # (row, col), counted from 0 at the top left
# TRAP_POSITIONS = [       # any number of traps, each (row, col)
#     (3, 4),

# ]
# TREASURE_POS = (4, 4)
# WALL_POSITIONS = [       # 5 walls, each (row, col). PLACEHOLDERS: replace with yours
#     (1, 1),
#     (1, 2),
#     (2, 2),
#     (3, 2),
#     (4, 2),
# ]
# START_COST = 1           # UCS only: the start cell's own cost (normally 0)
# TRAP_COST = 6            # UCS only: every trap can be walked through at this cost


START_POS = (0, 0)       # (row, col), counted from 0 at the top left
TRAP_POSITIONS = [       # any number of traps, each (row, col)
    (6, 7),
    (7, 6)
    
]
TREASURE_POS = (7, 7)
WALL_POSITIONS = [       # 5 walls, each (row, col). PLACEHOLDERS: replace with yours
    (6, 5),
    (6, 6),
    (6, 8),
    (6, 9),
    (7, 8),
    (8, 6),
    (8, 8)
]
START_COST = 1           # UCS only: the start cell's own cost (normally 0)
TRAP_COST = 6   

# -----------------------------------------------------------------------------


def build_custom_grid(start, traps, treasure, walls, size=GRID_SIZE):
    """Return a size x size grid with S, X, T and every wall at exactly the given spots.

    Raises ValueError for anything that cannot produce a valid grid: a position outside
    the grid, or two things (including two traps or two walls) on the same cell.
    """
    placements = [("start", start), ("treasure", treasure)]
    placements += [(f"trap {i + 1}", trap) for i, trap in enumerate(traps)]
    placements += [(f"wall {i + 1}", wall) for i, wall in enumerate(walls)]

    seen = {}
    for name, (row, col) in placements:
        if not (0 <= row < size and 0 <= col < size):
            raise ValueError(f"{name} {(row, col)} is outside the {size}x{size} grid")
        if (row, col) in seen:
            raise ValueError(f"{name} and {seen[(row, col)]} are both on {(row, col)}")
        seen[(row, col)] = name

    grid = [[EMPTY for _ in range(size)] for _ in range(size)]
    grid[start[0]][start[1]] = START
    grid[treasure[0]][treasure[1]] = TREASURE
    for row, col in traps:
        grid[row][col] = TRAP
    for row, col in walls:
        grid[row][col] = STATIC_WALLS
    return grid


def build_custom_weights(grid, start):
    """Random weights for open cells, but the start costs START_COST and every trap TRAP_COST."""
    weights = create_weight_matrix(grid)
    weights[start[0]][start[1]] = START_COST
    for r, row in enumerate(grid):
        for c, cell in enumerate(row):
            if cell == TRAP:
                weights[r][c] = TRAP_COST
    return weights


def main():
    # imported here so build_custom_grid can be used (and tested) without pygame
    from agents import Agent
    from algos.bfs import BFS
    from algos.dfs import DFS
    from algos.ucs import UCS
    from gui import ALGORITHMS, Gui
    from report import format_run_report

    grid = build_custom_grid(START_POS, TRAP_POSITIONS, TREASURE_POS, WALL_POSITIONS)
    agent = Agent(grid)
    state = {"weights": None}  # only exists while UCS is the selected algorithm

    def refresh_weights():
        if ALGORITHMS[gui.current_algo_idx] == "UCS":
            state["weights"] = build_custom_weights(grid, START_POS)
        else:
            state["weights"] = None
        gui.set_weights(state["weights"])

    def run_current_algorithm():
        algo_name = ALGORITHMS[gui.current_algo_idx]
        if algo_name == "DFS":
            algo = DFS()
        elif algo_name == "BFS":
            algo = BFS()
        elif algo_name == "UCS":
            if state["weights"] is None:
                refresh_weights()
            algo = UCS(state["weights"], unusual_costs=True)
        else:
            raise ValueError(f"Unknown algorithm: {algo_name}")

        visited, solution, seconds, cost, expanded = agent.run(algo)
        gui.set_solution_path(solution)
        gui.set_visited(visited)
        print(format_run_report(
            algo_name, solution, expanded, seconds, cost,
            state["weights"] if algo_name == "UCS" else None,
        ))

    def regenerate():
        # the layout is fixed; only the random weights change
        refresh_weights()
        return grid

    def algorithm_changed():
        refresh_weights()
        if state["weights"] is not None:
            # the old overlay was drawn for a different weight matrix
            gui.set_visited([])
            gui.set_solution_path([])

    gui = Gui(grid, regenerate, run_current_algorithm, on_algo_change=algorithm_changed)
    return gui


if __name__ == "__main__":
    main().run()
