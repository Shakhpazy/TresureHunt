LEGEND = "Coordinates are (row, col), counted from 0 at the top left corner."
WEIGHT_LEGEND = "w is the cost of stepping onto a cell (always 1 for DFS and BFS); total is the cost so far."


def format_run_report(algo_name, solution, nodes_expanded, execution_time, total_cost=None, weights=None):
    # DFS and BFS have no weight matrix, so every step onto a cell costs 1 and the start costs 0
    lines = [f"=== {algo_name} ===", LEGEND, WEIGHT_LEGEND]

    if solution:
        trail, path_cost = _format_cost_trail(solution, weights)
        lines.extend(trail)
        if total_cost is not None:
            path_cost = total_cost
        lines.append(f"Path cost: {path_cost}")
    else:
        lines.append("No path to the treasure")
        lines.append("Path cost: n/a")

    lines.append(f"Nodes expanded: {nodes_expanded}")
    lines.append(f"Runtime: {execution_time:.6f} seconds")
    return "\n".join(lines)


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
