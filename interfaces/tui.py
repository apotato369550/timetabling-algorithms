"""
Interactive Terminal UI for Timetabling Algorithm Testing

Provides menu-driven interface for:
- Algorithm selection
- Data loading (CSV or synthetic)
- Constraint configuration
- Algorithm execution
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
    from algorithms import load_algorithms

    algos = load_algorithms()
    algo_list = list(algos.keys())

    if not algo_list:
        console.print("[red]Error: No algorithms found[/red]")
        return None

    console.print("\n[bold]Available Algorithms:[/bold]")
    for i, name in enumerate(algo_list, 1):
        console.print(f"  {i}. {name}")

    choice = Prompt.ask("Select algorithm", choices=[str(i) for i in range(1, len(algo_list) + 1)])
    return algo_list[int(choice) - 1]

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

def run_algorithm(algo_name, problem):
    """Execute algorithm and display results"""
    from algorithms import get_algorithm
    from core import Statistics

    try:
        algo = get_algorithm(algo_name)
        meta = algo.metadata()

        console.print(f"\n[bold]Running: {meta['name']} (v{meta['version']})[/bold]")
        console.print(f"Problem size: {len(problem)} courses")

        # Simple constraints for now
        constraints = {
            'earliestStart': '08:00',
            'latestEnd': '18:00',
            'allowFull': False,
            'allowAt_risk': True,
            'maxSchedules': 5,
            'maxFullPerSchedule': 0
        }

        start = time.perf_counter()
        solutions = algo.solve(problem, constraints)
        elapsed = (time.perf_counter() - start) * 1000

        console.print(f"[green]✓ Found {len(solutions)} valid schedule(s) in {elapsed:.2f}ms[/green]")

        # Display results
        display_results(solutions, elapsed)

    except Exception as e:
        console.print(f"[red]✗ Algorithm error: {e}[/red]")

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

            # Step 3: Run
            run_algorithm(algo_name, problem)

            # Step 4: Continue?
            if not Confirm.ask("\n[bold]Run another test?[/bold]"):
                break

        except KeyboardInterrupt:
            console.print("\n[yellow]Interrupted[/yellow]")
            break
        except Exception as e:
            console.print(f"[red]Unexpected error: {e}[/red]")

    console.print("[dim]Goodbye![/dim]")
