"""
CP-SAT Wrapper for Timetabling Problem Verification

Provides a constraint satisfaction solver using Google OR-Tools CP-SAT.
Used as a verification tool to benchmark backtracking solutions against
an industrial-strength solver.

The solver takes a problem dictionary (course -> list of sections) and
returns feasible schedules that satisfy all hard constraints.
"""

import time
from typing import Dict, List, Optional
from ortools.sat.python import cp_model
from core.models import Section, Constraints
from core.parsing import parse_schedule_string


def solve_with_cpsat(
    problem: Dict[str, List[Section]],
    constraints: Optional[Constraints] = None,
    time_limit_s: float = 10.0
) -> Dict:
    """
    Solve timetabling problem using CP-SAT solver.

    Args:
        problem: Dictionary mapping course names to lists of Section objects
        constraints: Optional constraint dictionary (not used in basic solver,
                    but included for API compatibility)
        time_limit_s: Maximum solver time in seconds (default 10)

    Returns:
        Dictionary with keys:
        - feasible (bool): Whether a feasible solution was found
        - solution (dict): Mapping {course_name: selected_Section} if feasible
        - status (str): Solver status ('OPTIMAL', 'FEASIBLE', 'INFEASIBLE', 'UNKNOWN')
        - runtime_ms (float): Solver runtime in milliseconds
        - objective_value (float): Objective value (0 for feasibility only)
        - optimal (bool): Whether solution is proven optimal

    Example:
        problem = {
            'MATH_101': [Section(1, 'MW 10:00 AM - 11:30 AM', '15/30', 'OK')],
            'CS_101': [Section(1, 'TTh 10:00 AM - 11:30 AM', '20/30', 'OK')]
        }
        result = solve_with_cpsat(problem, time_limit_s=5)
        if result['feasible']:
            for course, section in result['solution'].items():
                print(f"{course}: {section.schedule}")
    """
    start_time = time.perf_counter()

    # Create model
    model = cp_model.CpModel()

    # Parse all schedules once
    parsed_schedules = {}
    for course_name, sections in problem.items():
        parsed_schedules[course_name] = []
        for section in sections:
            parsed = parse_schedule_string(section.schedule)
            if parsed is None:
                # If parsing fails, treat as infeasible
                return {
                    'feasible': False,
                    'solution': {},
                    'status': 'INFEASIBLE',
                    'runtime_ms': (time.perf_counter() - start_time) * 1000,
                    'objective_value': 0,
                    'optimal': False
                }
            parsed_schedules[course_name].append(parsed)

    # Create decision variables for each course
    # x[course][section_idx] = 1 if section is selected for that course
    selection_vars = {}
    for course_name, sections in problem.items():
        selection_vars[course_name] = []
        for section_idx in range(len(sections)):
            var = model.NewBoolVar(f'{course_name}_section_{section_idx}')
            selection_vars[course_name].append(var)

    # Constraint 1: Each course must have exactly one section selected
    for course_name, vars_list in selection_vars.items():
        model.Add(sum(vars_list) == 1)

    # Constraint 2: No time conflicts between selected sections
    course_names = list(problem.keys())
    for i in range(len(course_names)):
        for j in range(i + 1, len(course_names)):
            course_i = course_names[i]
            course_j = course_names[j]

            # For each pair of sections (one from each course)
            for sec_i_idx, sec_i in enumerate(problem[course_i]):
                for sec_j_idx, sec_j in enumerate(problem[course_j]):
                    # Check if these two sections conflict
                    if _has_time_conflict(
                        parsed_schedules[course_i][sec_i_idx],
                        parsed_schedules[course_j][sec_j_idx]
                    ):
                        # If they conflict, they can't both be selected
                        # (NOT (x_i AND x_j)) = (NOT x_i OR NOT x_j)
                        model.Add(
                            selection_vars[course_i][sec_i_idx]
                            + selection_vars[course_j][sec_j_idx] <= 1
                        )

    # Set solver parameters
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit_s
    solver.parameters.log_search_progress = False

    # Solve
    status = solver.Solve(model)

    # Extract solution
    feasible = status in (
        cp_model.OPTIMAL,
        cp_model.FEASIBLE
    )

    solution = {}
    if feasible:
        for course_name, vars_list in selection_vars.items():
            for section_idx, var in enumerate(vars_list):
                if solver.Value(var) == 1:
                    solution[course_name] = problem[course_name][section_idx]
                    break

    # Map status to string
    status_str = _status_to_string(status)

    end_time = time.perf_counter()
    runtime_ms = (end_time - start_time) * 1000

    return {
        'feasible': feasible,
        'solution': solution,
        'status': status_str,
        'runtime_ms': runtime_ms,
        'objective_value': 0,  # No optimization objective, just feasibility
        'optimal': status == cp_model.OPTIMAL
    }


def _has_time_conflict(parsed_schedule_a: Dict, parsed_schedule_b: Dict) -> bool:
    """
    Check if two parsed schedules have time conflicts.

    Args:
        parsed_schedule_a: Dict with 'days' and 'startTime'/'endTime' in minutes
        parsed_schedule_b: Same format

    Returns:
        True if schedules overlap in time
    """
    # Check if any day overlaps
    days_a = set(parsed_schedule_a['days'])
    days_b = set(parsed_schedule_b['days'])

    # If no common days, no conflict
    if not days_a.intersection(days_b):
        return False

    # If common days, check time overlap
    # Overlap if: start_a < end_b AND end_a > start_b
    start_a = parsed_schedule_a['startTime']
    end_a = parsed_schedule_a['endTime']
    start_b = parsed_schedule_b['startTime']
    end_b = parsed_schedule_b['endTime']

    return start_a < end_b and end_a > start_b


def _status_to_string(status: int) -> str:
    """Convert OR-Tools status code to string."""
    status_map = {
        0: 'OPTIMAL',           # cp_model.OPTIMAL
        1: 'FEASIBLE',          # cp_model.FEASIBLE
        2: 'INFEASIBLE',        # cp_model.INFEASIBLE
        3: 'UNKNOWN',           # cp_model.UNKNOWN
    }
    return status_map.get(status, 'UNKNOWN')
