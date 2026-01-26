#!/usr/bin/env python3
"""
Timetabling Algorithm Research Framework - Entry Point

Supports two modes:
  - CLI (scriptable): python3 main.py --algo backtracking_v1 --input data.csv --format json --output results.json
  - TUI (interactive): python3 main.py --interactive
"""

import sys
import argparse
import json
from typing import Optional, Dict, List, Any

def cli_mode(args):
    """Execute CLI mode (scriptable)"""
    from algorithms import get_algorithm
    from data_gen import load_csv, generate_problem
    from core import Statistics
    import time

    try:
        # Load algorithm
        algo = get_algorithm(args.algo)

        # Load data
        if args.generate:
            size, tightness = args.generate.split('_')
            problem = generate_problem(size, tightness)
        else:
            problem = load_csv(args.input)

        # Load constraints
        constraints = {
            'earliestStart': '08:00',
            'latestEnd': '18:00',
            'allowFull': False,
            'allowAt_risk': True,
            'maxSchedules': args.max_schedules or 5,
            'maxFullPerSchedule': 0
        }

        # Run
        start = time.perf_counter()
        solutions = algo.solve(problem, constraints)
        elapsed_ms = (time.perf_counter() - start) * 1000

        # Format output
        result = {
            'algorithm': algo.metadata()['name'],
            'problem_size': len(problem),
            'solutions_found': len(solutions),
            'runtime_ms': elapsed_ms,
            'status': 'success'
        }

        if args.format == 'json':
            output = json.dumps(result, indent=2)
        else:
            output = str(result)

        if args.output:
            with open(args.output, 'w') as f:
                f.write(output)
            print(f"Results written to {args.output}")
        else:
            print(output)

        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

def tui_mode():
    """Execute TUI mode (interactive)"""
    from interfaces.tui import run_interactive
    run_interactive()

def main():
    parser = argparse.ArgumentParser(
        description="Timetabling Algorithm Research Framework",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 main.py --interactive
  python3 main.py --algo backtracking_v1 --input courses.csv --format json --output results.json
  python3 main.py --algo backtracking_v1 --generate small_loose --max-schedules 10
        """
    )

    parser.add_argument('--interactive', action='store_true',
                        help='Interactive TUI mode')
    parser.add_argument('--algo', type=str,
                        help='Algorithm name (e.g., "Backtracking V1")')
    parser.add_argument('--input', type=str,
                        help='Input CSV file')
    parser.add_argument('--generate', type=str,
                        help='Generate synthetic problem (e.g., "small_loose", "medium_tight")')
    parser.add_argument('--format', choices=['json', 'text'], default='json',
                        help='Output format')
    parser.add_argument('--output', type=str,
                        help='Output file (default: stdout)')
    parser.add_argument('--max-schedules', type=int,
                        help='Max schedules to find')

    args = parser.parse_args()

    if args.interactive:
        tui_mode()
        return 0
    elif args.algo:
        return cli_mode(args)
    else:
        parser.print_help()
        return 1

if __name__ == '__main__':
    sys.exit(main())
