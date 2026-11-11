LEGEND = "Coordinates are (row, col), counted from 0 at the top left corner."
WEIGHT_LEGEND = "w is the cost of stepping onto a cell (always 1 for DFS and BFS); total is the cost so far."


def format_run_report(
    algo_name, solutions, nodes_expanded, execution_time, total_cost=None, weights=None,
    heuristic_values=None,
):
    # DFS and BFS have no weight matrix, so every step onto a cell costs 1 and the start costs 0
    lines = [f"=== {algo_name} ===", LEGEND, WEIGHT_LEGEND]

    if solutions:
        # Accept both the original single path and the newer list of paths.
        first = solutions[0]
        paths = [solutions] if _is_coordinate(first) else solutions

        path_cost = 0
        for treasure_number, solution in enumerate(paths, start=1):
            lines.append(f"Path to treasure {treasure_number}:")
            trail, solution_cost = _format_cost_trail(solution, weights)
            lines.extend(trail)
            path_cost += solution_cost
        if total_cost is not None:
            path_cost = total_cost
        cost_line = f"Path cost: {path_cost}"
    else:
        lines.append("No path to the treasure")
        cost_line = "Path cost: n/a"

    if heuristic_values is not None:  # only A* and GBFS have any
        lines.append("h of each expanded cell, in the order they were expanded:")
        lines.extend(f"h({r}, {c}) = {h}" for (r, c), h in heuristic_values)
        lines.append(f"Heuristic values: {sum(h for _, h in heuristic_values)}")
    lines.append(cost_line)

    lines.append(f"Nodes expanded: {nodes_expanded}")
    lines.append(f"Runtime: {execution_time:.6f} seconds")
    
    return "\n".join(lines)


def _is_coordinate(value):
    return (
        isinstance(value, (tuple, list))
        and len(value) == 2
        and all(isinstance(number, int) for number in value)
    )


def _format_cost_trail(solution, weights):
    trail = []
    running_cost = 0
    for number, (r, c) in enumerate(solution):
        if weights is not None:
            step_cost = weights[r][c]
        else:
            step_cost = 0 if number == 0 else 1
        running_cost += step_cost
        trail.append(f"({r}, {c}) w:{step_cost} -> total {running_cost}")
    return trail, running_cost
