"""
Output Formatting Module

Provides utilities for formatting algorithm results and comparison tables.
Supports both rich and plain text output.
"""

from typing import Dict, Any


def format_verification_comparison_table(
    backtracking_result: Dict[str, Any],
    cpsat_result: Dict[str, Any]
) -> str:
    """
    Format comparison of backtracking vs CP-SAT results as ASCII table.

    Args:
        backtracking_result: Dictionary with keys:
            - runtime_ms (float)
            - feasible (bool)
            - solution_count (int)
            - status (str)
        cpsat_result: Dictionary with keys:
            - runtime_ms (float)
            - feasible (bool)
            - status (str)
            - optimal (bool)

    Returns:
        Formatted ASCII table string
    """
    lines = []
    lines.append("")
    lines.append("=" * 80)
    lines.append("ALGORITHM VERIFICATION COMPARISON")
    lines.append("=" * 80)

    # Headers
    lines.append(f"{'Metric':<25} {'Backtracking':<25} {'CP-SAT':<25}")
    lines.append("-" * 80)

    # Runtime
    bt_runtime = f"{backtracking_result['runtime_ms']:.2f} ms"
    cpsat_runtime = f"{cpsat_result['runtime_ms']:.2f} ms"
    lines.append(f"{'Runtime':<25} {bt_runtime:<25} {cpsat_runtime:<25}")

    # Feasibility
    bt_feasible = "Yes" if backtracking_result['feasible'] else "No"
    cpsat_feasible = "Yes" if cpsat_result['feasible'] else "No"
    match_marker = "✓" if backtracking_result['feasible'] == cpsat_result['feasible'] else "✗"
    lines.append(f"{'Feasible':<25} {bt_feasible:<25} {cpsat_feasible:<25} {match_marker}")

    # Solution Count
    bt_count = str(backtracking_result.get('solution_count', 0))
    cpsat_count = "1" if cpsat_result['feasible'] else "0"
    lines.append(f"{'Solutions Found':<25} {bt_count:<25} {cpsat_count:<25}")

    # Status
    lines.append(f"{'Status':<25} {backtracking_result['status']:<25} {cpsat_result['status']:<25}")

    # Optimality
    optimal_status = "Yes" if cpsat_result.get('optimal', False) else "No"
    lines.append(f"{'Proven Optimal':<25} {'N/A':<25} {optimal_status:<25}")

    lines.append("=" * 80)
    lines.append("")

    return "\n".join(lines)


def format_verification_comparison(
    backtracking_result: Dict[str, Any],
    cpsat_result: Dict[str, Any]
):
    """
    Format comparison of backtracking vs CP-SAT results.
    
    Tries to use Rich if available, falls back to ASCII table.

    Args:
        backtracking_result: Dictionary with backtracking result data
        cpsat_result: Dictionary with CP-SAT result data

    Returns:
        Rich Table or string (depending on availability)
    """
    try:
        from rich.table import Table

        table = Table(title="Algorithm Verification Comparison", border_style="blue")

        table.add_column("Metric", style="cyan", width=20)
        table.add_column("Backtracking", style="magenta", width=20)
        table.add_column("CP-SAT", style="yellow", width=20)

        # Runtime
        bt_runtime = f"{backtracking_result['runtime_ms']:.2f} ms"
        cpsat_runtime = f"{cpsat_result['runtime_ms']:.2f} ms"
        table.add_row("Runtime", bt_runtime, cpsat_runtime)

        # Feasibility
        bt_feasible = "Yes" if backtracking_result['feasible'] else "No"
        cpsat_feasible = "Yes" if cpsat_result['feasible'] else "No"

        # Color-code based on match
        if backtracking_result['feasible'] == cpsat_result['feasible']:
            table.add_row("Feasible", f"[green]{bt_feasible}[/green]", f"[green]{cpsat_feasible}[/green]")
        else:
            table.add_row("Feasible", f"[red]{bt_feasible}[/red]", f"[red]{cpsat_feasible}[/red]")

        # Solution Count
        bt_count = str(backtracking_result.get('solution_count', 0))
        cpsat_count = "1" if cpsat_result['feasible'] else "0"
        table.add_row("Solutions Found", bt_count, cpsat_count)

        # Status
        table.add_row("Status", backtracking_result['status'], cpsat_result['status'])

        # Optimality
        optimal_status = "Yes" if cpsat_result.get('optimal', False) else "No"
        table.add_row("Proven Optimal", "N/A", optimal_status)

        return table

    except ImportError:
        # Rich not available, return ASCII table
        return format_verification_comparison_table(backtracking_result, cpsat_result)


def format_results_summary(solutions: list, elapsed_ms: float, problem_size: int) -> str:
    """
    Format basic algorithm results summary as ASCII table.

    Args:
        solutions: List of solution dictionaries
        elapsed_ms: Runtime in milliseconds
        problem_size: Number of courses in problem

    Returns:
        Formatted string
    """
    lines = []
    lines.append("")
    lines.append("=" * 60)
    lines.append("RESULTS SUMMARY")
    lines.append("=" * 60)
    lines.append(f"{'Problem Size':<30} {problem_size} courses")
    lines.append(f"{'Solutions Found':<30} {len(solutions)}")
    lines.append(f"{'Runtime':<30} {elapsed_ms:.2f} ms")

    if solutions:
        avg_courses = sum(len(sol.get('selections', [])) for sol in solutions) / len(solutions)
        lines.append(f"{'Avg Courses/Schedule':<30} {avg_courses:.1f}")

    lines.append("=" * 60)
    lines.append("")

    return "\n".join(lines)


def format_solution_table(solutions: list, max_display: int = 5) -> str:
    """
    Format solution details in table format.

    Args:
        solutions: List of solution dictionaries
        max_display: Maximum number of solutions to display

    Returns:
        Formatted string
    """
    if not solutions:
        return "No solutions found"

    lines = []
    lines.append("")
    lines.append("=" * 80)
    lines.append(f"SOLUTIONS (showing {min(len(solutions), max_display)} of {len(solutions)})")
    lines.append("=" * 80)

    # Headers
    lines.append(f"{'Schedule #':<15} {'Courses':<15} {'Full Sections':<15} {'Ends By 6PM':<15}")
    lines.append("-" * 80)

    for i, sol in enumerate(solutions[:max_display], 1):
        num_courses = len(sol.get('selections', []))
        meta = sol.get('meta', {})
        full_count = meta.get('fullCount', 0)
        ends_early = "Yes" if meta.get('endsByPreferred', False) else "No"

        lines.append(f"{str(i):<15} {str(num_courses):<15} {str(full_count):<15} {ends_early:<15}")

    lines.append("=" * 80)
    lines.append("")

    return "\n".join(lines)
