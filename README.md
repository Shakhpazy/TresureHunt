# TresureHunt
This is for TCSS 435 AI

## Quick start

Needs **Python 3.10 or newer**. From the project folder:

```bash
python3 -m venv .venv                      # Windows: py -m venv .venv
source .venv/bin/activate                  # Windows: .venv\Scripts\activate
python -m pip install -r requirements.txt
python main.py
```

If `python3 --version` is older than 3.10, create the environment with a newer interpreter instead (for example `python3.13 -m venv .venv`). More detail is in the setup sections below.

In the window, choose an algorithm from the **Algorithm** dropdown, click **Run**, and read the report in the terminal.

## Grid generation

Each run creates a fixed 10x10 map. 15 of its cells are static walls, and each map also has one start, one trap and one treasure. Select **Regenerate Grid** to generate a new map.

## Algorithms

Choose an algorithm from the **Algorithm** dropdown in the sidebar (click it to open the list, click a name to pick it; click elsewhere or press Esc to close it), then click **Run**. Green cells are the cells the search reached and the white dots mark the path it found.

All three searches share one interface (`algos/search_algo.py`): `search(grid, start_row, start_col)` returns the parent of every cell it reached, the treasure's location (`()` if it cannot be reached) and the number of nodes expanded. UCS also returns its total cost. `agents.py` rebuilds the path by following the parents from the treasure back to the start. None of them can step on a wall (`#`), a trap (`X`) or off the grid.

The console outputs below all come from the same map (`S` start, `T` treasure, `#` wall, `X` trap):

```
. . # # . . . . . .
. . . . T . . . . #
# . . . # # # . . .
# . . . # . . . . .
. . . . . . . . . .
. . . . S . . . . .
. . . . . . . . . .
# . . . . . # # . .
X . . . . # . . . #
. . . . . . . # . .
```

### DFS (depth-first search, `algos/dfs.py`)

- It uses a stack of `(cell, parent)` pairs. A cell is marked visited when it is **popped**, not when it is pushed. The same cell can sit on the stack more than once, and a copy popped after the cell is already visited is skipped.
- The last neighbor pushed is the first one popped, so it explores left, up, right, then down, going as deep as it can before backing up.
- It stops when it pops the treasure. The path it returns is simply the first one it found, not the shortest: 12 steps below, where BFS needs 6.

```
=== DFS ===
Coordinates are (row, col), counted from 0 at the top left corner.
w is the cost of stepping onto a cell (always 1 for DFS and BFS); total is the cost so far.
(5, 4) w:0 -> total 0
(5, 3) w:1 -> total 1
(5, 2) w:1 -> total 2
(5, 1) w:1 -> total 3
(5, 0) w:1 -> total 4
(4, 0) w:1 -> total 5
(4, 1) w:1 -> total 6
(3, 1) w:1 -> total 7
(2, 1) w:1 -> total 8
(1, 1) w:1 -> total 9
(1, 2) w:1 -> total 10
(1, 3) w:1 -> total 11
(1, 4) w:1 -> total 12
Path cost: 12
Nodes expanded: 16
Runtime: 0.000013 seconds
```

### BFS (breadth-first search, `algos/bfs.py`)

- It uses a queue and works level by level: every cell 1 step away, then every cell 2 steps away, and so on. A cell is marked when it is **queued**, so each cell is queued once and its parent is recorded at that moment.
- Because a whole level is finished before the next starts, the first time it reaches the treasure is by a path with the fewest steps.
- Nodes expanded counts each cell taken off the queue. Cells that were queued but never taken off still show green, so the green area can be a little bigger than the expanded count.

```
=== BFS ===
Coordinates are (row, col), counted from 0 at the top left corner.
w is the cost of stepping onto a cell (always 1 for DFS and BFS); total is the cost so far.
(5, 4) w:0 -> total 0
(4, 4) w:1 -> total 1
(4, 3) w:1 -> total 2
(3, 3) w:1 -> total 3
(2, 3) w:1 -> total 4
(1, 3) w:1 -> total 5
(1, 4) w:1 -> total 6
Path cost: 6
Nodes expanded: 57
Runtime: 0.000033 seconds
```

### UCS (uniform cost search, `algos/ucs.py`)

- UCS uses step costs. Choosing UCS lays a weight matrix over the current map and draws it as `w:number` in each cell: empty cells and the treasure get a random cost from 1 to 99, the start costs 0, and traps and walls cannot be entered. Choosing UCS again in the dropdown, or clicking **Regenerate Grid** while UCS is selected, creates new weights. DFS and BFS never see the weights.
- It uses a priority queue (min-heap) ordered by the cost so far, then row, then column. A cell is marked visited when it is **popped**, because the first time a cell is popped it was reached by its cheapest route. Later, more expensive copies are skipped.
- It returns the cheapest path, which is not always the one with the fewest steps: below it takes 10 steps for a cost of 269, while BFS's 6-step path would cost 340 with these weights.
- It checks its weights before searching and raises a `ValueError` if they do not match the grid, if a weight below 1 is found (the start is the only 0), or if a wall or trap has a weight.

```
=== UCS ===
Coordinates are (row, col), counted from 0 at the top left corner.
w is the cost of stepping onto a cell (always 1 for DFS and BFS); total is the cost so far.
(5, 4) w:0 -> total 0
(6, 4) w:23 -> total 23
(6, 3) w:19 -> total 42
(6, 2) w:2 -> total 44
(5, 2) w:27 -> total 71
(4, 2) w:7 -> total 78
(3, 2) w:4 -> total 82
(2, 2) w:45 -> total 127
(2, 3) w:34 -> total 161
(1, 3) w:11 -> total 172
(1, 4) w:97 -> total 269
Path cost: 269
Nodes expanded: 60
Runtime: 0.000056 seconds
```

### Reading the output

- Each path line is one cell: its `(row, col)`, the cost of stepping onto it, and the cost so far. The start costs 0, and DFS and BFS charge 1 per step.
- **Path cost** is the total cost of the path (`n/a` when the treasure cannot be reached, which also prints `No path to the treasure`).
- **Nodes expanded** is how many cells the search took off its frontier and expanded, counting the treasure cell when it is reached. It is not the same as the path length.
- **Runtime** is the time spent inside the search, in seconds. Runtimes and UCS weights change from run to run.

## Sample Grid

Example 1:

![Example 1](images/GridExample1.png)

Example 2:

![Example 2](images/GridExample2.png)

Example 3:

![Example 3](images/GridExample3.png)

## Requirements

**Python 3.10 or newer** (developed on 3.13). The code uses the `X | Y` type-union syntax, which raises a `TypeError` on Python 3.9 and older. Check your version with:

```bash
python3 --version   # macOS / Linux
py --version        # Windows
```

If it is older than 3.10, install a newer Python from [python.org](https://www.python.org/downloads/) (or `brew install python@3.13` on macOS) before continuing. The `.python-version` file records the version the project was developed with, for tools like `pyenv` and `uv`.

## Set up the virtual environment

Run these commands from the project folder. A virtual environment is tied to the Python that created it, so create it with a 3.10+ interpreter. If you have an old `.venv` from an older Python, delete it first (`rm -rf .venv` on macOS, `rmdir /s /q .venv` on Windows).

### Windows

Create the environment:

```powershell
py -3.13 -m venv .venv
```

Use any installed 3.10+ version in place of `3.13`.

Activate it in PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Or activate it in Command Prompt:

```bat
.venv\Scripts\activate.bat
```

### macOS

Create the environment:

```bash
python3.13 -m venv .venv
```

Use `python3` instead if `python3 --version` already reports 3.10 or newer, or substitute any installed 3.10+ version for `3.13`.

Activate it:

```bash
source .venv/bin/activate
```

### Install dependencies

With the virtual environment activated, install the dependencies (Pygame) listed in `requirements.txt`:

```sh
python -m pip install -r requirements.txt
```

### Run the game

From the project folder, with the virtual environment activated, run:

```sh
python main.py
```

### Run the tests (optional)

The tests are only for development, so they have their own requirements file and the game does not need them. With the virtual environment activated:

```sh
python -m pip install -r requirements-dev.txt
python -m pytest
```

There is one test file per search in `tests/` (`test_dfs.py`, `test_bfs.py`, `test_ucs.py`), each with three hand-made grids.

To exit the environment on either platform, run:

```bash
deactivate
```
