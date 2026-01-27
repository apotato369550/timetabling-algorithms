"""
Interactive Terminal UI for Timetabling Algorithm Testing

Provides menu-driven interface for:
- Algorithm selection
- Data loading (CSV or synthetic)
- Constraint configuration
- Algorithm execution with optional verification
- Results visualization
"""

from typing import Dict, List, Optional
from rich.console import Console
from rich.table import Table
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
import json
import time

console = Console()

def display_header():
    """Display application header"""
    console.print(Panel.fit(
        "[bold cyan]Timetabling Algorithm Research Framework[/bold cyan]",
        border_style="blue"
    ))

def select_algorithm():
    """Prompt user to select algorithm"""
    console.print("\n[bold]Available Algorithms:[/bold]")
    console.print("  1. Backtracking V1")

    choice = Prompt.ask("Select algorithm", choices=["1"])
    return "Backtracking V1"

def select_data_source():
    """Prompt user for data source (CSV or synthetic)"""
    console.print("\n[bold]Data Source:[/bold]")
    console.print("  1. Load from CSV")
    console.print("  2. Generate synthetic")

    choice = Prompt.ask("Select data source", choices=["1", "2"])
    return choice

def load_data_csv():
    """Prompt for CSV file path and load"""
    from data_gen import load_csv

    filepath = Prompt.ask("Enter CSV file path")
    try:
        problem = load_csv(filepath)
        console.print(f"[green]✓ Loaded {len(problem)} courses from CSV[/green]")
        return problem
    except Exception as e:
        console.print(f"[red]✗ Error loading CSV: {e}[/red]")
        return None

def load_data_synthetic():
    """Prompt for synthetic problem parameters"""
    from data_gen import generate_problem

    size = Prompt.ask("Problem size", choices=["small", "medium", "large"])
    tightness = Prompt.ask("Constraint tightness", choices=["loose", "tight"])
    seed = Prompt.ask("Random seed (optional, press Enter for random)", default="")

    seed_int = int(seed) if seed else None
    problem = generate_problem(size, tightness, seed=seed_int)
    console.print(f"[green]✓ Generated {len(problem)} courses[/green]")
    return problem

def select_run_mode():
    """Prompt user to select run mode (with or without verification)"""
    console.print("\n[bold]Run Mode:[/bold]")
    console.print("  1. Standard (Backtracking only)")
    console.print("  2. With Verification (Backtracking + CP-SAT comparison)")

    choice = Prompt.ask("Select run mode", choices=["1", "2"])
    return choice == "2"

def run_algorithm(algo_name, problem, verify=False):
    """Execute algorithm and optionally verify with CP-SAT"""
    from scheduler.scheduler_engine import generate_schedules
    from verification.cpsat_wrapper import solve_with_cpsat
    from interfaces.output import format_verification_comparison

    try:
        console.print(f"\n[bold]Running: Backtracking V1[/bold]")
        console.print(f"Problem size: {len(problem)} courses")

        # Setup constraints
        constraints = {
            'earliestStart': '08:00',
            'latestEnd': '18:00',
            'allowFull': False,
            'allowAt_risk': True,
            'maxSchedules': 5,
            'maxFullPerSchedule': 0
        }

        # Run backtracking
        start = time.perf_counter()
        solutions, stats = generate_schedules(
            list(problem.values()),
            constraints,
            enable_tracing=False
        )
        bt_elapsed = (time.perf_counter() - start) * 1000

        console.print(f"[green]✓ Found {len(solutions)} valid schedule(s) in {bt_elapsed:.2f}ms[/green]")

        # If verification requested, run CP-SAT
        if verify:
            console.print(f"\n[bold]Running verification with CP-SAT...[/bold]")

            cpsat_result = solve_with_cpsat(problem, time_limit_s=10)

            console.print(f"[green]✓ CP-SAT completed in {cpsat_result['runtime_ms']:.2f}ms[/green]")

            # Build comparison result dicts
            bt_result = {
                'runtime_ms': bt_elapsed,
                'feasible': len(solutions) > 0,
                'solution_count': len(solutions),
                'status': 'FEASIBLE' if len(solutions) > 0 else 'INFEASIBLE'
            }

            # Display comparison table
            comparison = format_verification_comparison(bt_result, cpsat_result)
            if isinstance(comparison, str):
                # ASCII table
                console.print(comparison)
            else:
                # Rich table
                console.print(comparison)

            # Check for mismatch
            if bt_result['feasible'] != cpsat_result['feasible']:
                console.print(
                    "[yellow]⚠ Feasibility mismatch between algorithms[/yellow]"
                )

        # Display results table
        display_results(solutions, bt_elapsed)

    except Exception as e:
        console.print(f"[red]✗ Algorithm error: {e}[/red]")
        import traceback
        traceback.print_exc()

def display_results(solutions, elapsed_ms):
    """Display algorithm results"""
    if not solutions:
        console.print("[yellow]No solutions found[/yellow]")
        return

    table = Table(title="Solutions Summary")
    table.add_column("Schedule #", style="cyan")
    table.add_column("Courses", style="magenta")
    table.add_column("Status", style="green")

    for i, sol in enumerate(solutions, 1):
        num_courses = len(sol.get('selections', []))
        table.add_row(str(i), str(num_courses), "Valid")

    console.print(table)
    console.print(f"\n[dim]Total time: {elapsed_ms:.2f}ms[/dim]")

def run_interactive():
    """Main interactive loop"""
    display_header()

    while True:
        try:
            # Step 1: Select algorithm
            algo_name = select_algorithm()
            if not algo_name:
                break

            # Step 2: Load data
            source = select_data_source()
            if source == "1":
                problem = load_data_csv()
            else:
                problem = load_data_synthetic()

            if not problem:
                continue

            # Step 3: Select run mode (standard or with verification)
            verify = select_run_mode()

            # Step 4: Run
            run_algorithm(algo_name, problem, verify=verify)

            # Step 5: Continue?
            if not Confirm.ask("\n[bold]Run another test?[/bold]"):
                break

        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted[/yellow]")
            break
        except Exception as e:
            console.print(f"[red]Unexpected error: {e}[/red]")
            import traceback
            traceback.print_exc()

    console.print("[dim]Goodbye![/dim]")
