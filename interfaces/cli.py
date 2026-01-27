"""
Command-Line Interface for Timetabling Algorithm Testing

Supports scriptable execution with optional verification.

Usage:
  python3 main.py --algo backtracking_v1 --input courses.csv --format json --output results.json
  python3 main.py --algo backtracking_v1 --input courses.csv --verify
  python3 main.py --algo backtracking_v1 --generate small_loose --verify
"""

import sys
import json
import time
from typing import Optional, Dict, Any


def run_cli(args) -> int:
    """
    Execute CLI mode (scriptable).

    Args:
        args: Parsed command-line arguments

    Returns:
        Exit code (0 for success, 1 for failure)
    """
    from scheduler.scheduler_engine import generate_schedules
    from data_gen import load_csv, generate_problem
    from core.models import Constraints
    from verification.cpsat_wrapper import solve_with_cpsat
    from interfaces.output import format_verification_comparison

    try:
        # Load algorithm - for now we use backtracking directly
        # (Can be extended to load other algorithms)
        algo_name = args.algo.lower()
        if 'backtracking' not in algo_name:
            print(f"Error: Only 'backtracking_v1' supported in CLI", file=sys.stderr)
            return 1

        # Load data
        if args.generate:
            size, tightness = args.generate.split('_')
            problem = generate_problem(size, tightness)
            print(f"✓ Generated {len(problem)} courses ({size}, {tightness})")
        elif args.input:
            problem = load_csv(args.input)
            print(f"✓ Loaded {len(problem)} courses from {args.input}")
        else:
            print("Error: Must provide --input or --generate", file=sys.stderr)
            return 1

        # Setup constraints
        constraints: Constraints = {
            'earliestStart': '08:00',
            'latestEnd': '18:00',
            'allowFull': False,
            'allowAt_risk': True,
            'maxSchedules': args.max_schedules or 5,
            'maxFullPerSchedule': 0
        }

        # Run backtracking
        print(f"\nRunning: Backtracking V1")
        print(f"Problem size: {len(problem)} courses")

        start = time.perf_counter()
        solutions, stats = generate_schedules(
            list(problem.values()),
            constraints,
            enable_tracing=False
        )
        bt_elapsed_ms = (time.perf_counter() - start) * 1000

        bt_result = {
            'algorithm': 'Backtracking V1',
            'runtime_ms': bt_elapsed_ms,
            'feasible': len(solutions) > 0,
            'solution_count': len(solutions),
            'status': 'FEASIBLE' if len(solutions) > 0 else 'INFEASIBLE'
        }

        print(f"✓ Found {len(solutions)} valid schedule(s) in {bt_elapsed_ms:.2f}ms")

        # If --verify flag, run CP-SAT verification
        if args.verify:
            print(f"\nRunning verification with CP-SAT...")

            cpsat_result = solve_with_cpsat(problem, time_limit_s=args.verify_timeout or 10)

            print(f"✓ CP-SAT completed in {cpsat_result['runtime_ms']:.2f}ms")

            # Display comparison table
            comparison = format_verification_comparison(bt_result, cpsat_result)
            if isinstance(comparison, str):
                # ASCII table
                print(comparison)
            else:
                # Rich table - convert to string
                from io import StringIO
                import sys
                buffer = StringIO()
                from rich.console import Console
                temp_console = Console(file=buffer)
                temp_console.print(comparison)
                print(buffer.getvalue())

            # Check if results match
            if bt_result['feasible'] != cpsat_result['feasible']:
                print("Warning: Feasibility mismatch between algorithms")

            # Include verification in output
            output_data = {
                'problem_size': len(problem),
                'backtracking': bt_result,
                'cpsat': {
                    'runtime_ms': cpsat_result['runtime_ms'],
                    'feasible': cpsat_result['feasible'],
                    'status': cpsat_result['status'],
                    'optimal': cpsat_result['optimal']
                }
            }
        else:
            # Standard output without verification
            output_data = {
                'problem_size': len(problem),
                'algorithm': bt_result['algorithm'],
                'runtime_ms': bt_result['runtime_ms'],
                'solutions_found': bt_result['solution_count'],
                'status': bt_result['status']
            }

        # Format and output results
        if args.format == 'json':
            output = json.dumps(output_data, indent=2)
        else:
            output = str(output_data)

        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"\nResults written to {args.output}")
        else:
            if args.format == 'json':
                # Pretty print JSON to console
                print(json.dumps(output_data, indent=2))
            else:
                print(output)

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1
