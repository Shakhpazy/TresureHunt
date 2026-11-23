from collections import namedtuple

from agents import Agent
from grid import EMPTY, START, STATIC_WALLS, TRAP, TREASURE

SYMBOLS = {"S": START, "T": TREASURE, "#": STATIC_WALLS, "X": TRAP, ".": EMPTY}

Result = namedtuple("Result", ["path", "visited", "nodes_expanded", "total_cost"])


def make_grid(*rows):
    """Build a grid from text rows: S start, T treasure, # wall, X trap, . empty."""
    return [[SYMBOLS[symbol] for symbol in row] for row in rows]


def run_search(algo, grid):
    # These are the original first-treasure algorithm tests. Agent.run now
    # requests all treasures; that interface is covered in test_agent_paths.
    agent = Agent(grid)
    visited, treasure, nodes_expanded, *extra = algo.search(grid, agent.startr, agent.startc)
    path = agent._getSolutionPath(visited, treasure)
    total_cost = extra[0] if extra else None
    return Result(path, set(visited), nodes_expanded, total_cost)


def assert_valid_path(grid, path):
    """The path starts on S, ends on T, moves one cell at a time and never enters a wall or trap."""
    assert grid[path[0][0]][path[0][1]] == START
    assert grid[path[-1][0]][path[-1][1]] == TREASURE
    for (r1, c1), (r2, c2) in zip(path, path[1:]):
        assert abs(r1 - r2) + abs(c1 - c2) == 1
    for r, c in path:
        assert grid[r][c] not in (STATIC_WALLS, TRAP)
