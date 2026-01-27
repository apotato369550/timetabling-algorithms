#!/usr/bin/env python3
"""
Timetabling Algorithm Research Framework - Entry Point

Supports two modes:
  - CLI (scriptable): python3 main.py --algo backtracking_v1 --input data.csv --format json --output results.json
  - TUI (interactive): python3 main.py --interactive

With verification:
  - python3 main.py --algo backtracking_v1 --generate small_loose --verify
"""

import sys
import argparse
from typing import Optional, Dict, List, Any

def cli_mode(args):
    """Execute CLI mode (scriptable)"""
    from interfaces.cli import run_cli
    return run_cli(args)

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
  python3 main.py --algo backtracking_v1 --generate small_loose --verify
  python3 main.py --algo backtracking_v1 --generate medium_tight --verify --verify-timeout 15
        """
    )

    parser.add_argument('--interactive', action='store_true',
                        help='Interactive TUI mode')
    parser.add_argument('--algo', type=str,
                        help='Algorithm name (e.g., "backtracking_v1")')
    parser.add_argument('--input', type=str,
                        help='Input CSV file')
    parser.add_argument('--generate', type=str,
                        help='Generate synthetic problem (e.g., "small_loose", "medium_tight")')
    parser.add_argument('--verify', action='store_true',
                        help='Verify backtracking solution with CP-SAT solver')
    parser.add_argument('--verify-timeout', type=float, default=10.0,
                        help='CP-SAT solver timeout in seconds (default: 10)')
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
