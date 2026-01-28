# Timetabling Algorithm Research Framework

A research framework for investigating algorithmic approaches to timetabling (course scheduling) problems. This project compares backtracking with intelligent pruning against industrial-strength constraint solvers (OR-Tools CP-SAT) to understand when each approach excels.

## Current Status & Features

### Implemented Algorithms
- **Backtracking V1**: Recursive search with conflict-based pruning (baseline implementation, no heuristics)

### Data Sources
- **CSV Loading**: Import course sections from CSV files with flexible column mapping
- **Synthetic Generation**: Generate reproducible test problems at three sizes (small: 5 courses, medium: 20, large: 50) and two tightness levels (loose: 3-5 sections/course, tight: 2 sections/course)

### Verification & Analysis
- **CP-SAT Solver**: Verify backtracking results against OR-Tools constraint solver with configurable time limits
- **Execution Statistics**: Track search metrics (nodes explored, pruning effectiveness, runtime)
- **Optional Tracing**: Detailed decision logs for algorithm analysis

### Output Formats
- JSON: Structured output with complete metadata
- Text: Human-readable dictionary representation

## Setup Instructions

### Environment Requirements
- Python 3.8+
- pip package manager

### Installation

1. Navigate to the project directory:
```bash
cd /path/to/timetabling-algorithms
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

Required packages:
- `ortools` (for CP-SAT verification)
- `pyyaml` (for configuration files)
- `rich` (for TUI colored output)

### Verify Installation

```bash
python3 -m pytest test_scheduler.py -v
```

Expected output: All tests pass with green checkmarks.

## Usage Patterns

### CLI Mode (Scriptable, for Batch Processing)

Use the command-line interface for automated, non-interactive execution with output to files.

**Basic Syntax**:
```bash
python3 main.py --algo <algorithm> --input <csv_file> [--options]
```

**Arguments**:
- `--algo`: Algorithm to use (currently: `backtracking_v1`)
- `--input`: Path to CSV file with course sections
- `--generate`: Generate synthetic problem instead of loading CSV (format: `size_tightness`)
- `--verify`: Run CP-SAT verification after backtracking
- `--verify-timeout`: CP-SAT timeout in seconds (default: 10)
- `--format`: Output format: `json` or `text` (default: `text`)
- `--output`: Output file path (default: stdout)
- `--max-schedules`: Maximum schedules to find (default: 50)

### TUI Mode (Interactive, for Exploration)

Use the interactive terminal UI for guided exploration with menu-driven workflow.

**Launch Interactive Mode**:
```bash
python3 main.py --interactive
```

**Workflow Steps**:
1. Select algorithm (currently: Backtracking V1)
2. Choose data source: CSV file or synthetic generation
3. If synthetic: enter size (small/medium/large) and tightness (loose/tight)
4. Choose run mode: standard or with CP-SAT verification
5. View results with colored output and comparison table
6. Repeat with different dataset or exit

**Example Interactive Session**:
```
Welcome to Timetabling Algorithm Research Framework
┌─────────────────────────────────────────┐
│ Select Algorithm                        │
├─────────────────────────────────────────┤
│ 1. Backtracking V1                      │
│ 2. Exit                                 │
└─────────────────────────────────────────┘

Choose data source:
1. Load from CSV
2. Generate synthetic
3. Back

Generate problem:
Size: (small/medium/large): small
Tightness: (loose/tight): loose

Run mode:
1. Standard
2. With CP-SAT Verification
3. Back

Results:
Backtracking V1: Found 5 schedules in 12ms
CP-SAT Solver: Found 1 optimal in 45ms
[Comparison table...]
```

## Quick Examples

### Example 1: Generate Small Problem and Run Backtracking

```bash
python3 main.py --algo backtracking_v1 --generate small_loose
```

Output: Displays results to console showing number of schedules found and runtime.

### Example 2: Load CSV and Output to JSON File

```bash
python3 main.py --algo backtracking_v1 --input courses.csv --format json --output results.json
```

Loads sections from `courses.csv` and writes structured output to `results.json`.

### Example 3: Generate Medium Problem with Verification

```bash
python3 main.py --algo backtracking_v1 --generate medium_tight --verify --verify-timeout 15 --format json --output comparison.json
```

Generates 20 courses with tight constraints, runs both backtracking and CP-SAT (15s timeout), outputs to JSON.

### Example 4: Load Real Data with Constraints

```bash
python3 main.py --algo backtracking_v1 --input real_courses.csv --max-schedules 10 --format text
```

Loads real university course data, finds up to 10 valid schedules, outputs as text.

### Example 5: Interactive Exploration

```bash
python3 main.py --interactive
```

Launches the TUI where you navigate menus to select algorithm, data source, and run mode.

### Example 6: Run Tests

```bash
python3 test_scheduler.py
```

Or with pytest:
```bash
python3 -m pytest test_scheduler.py -v
```

## Data Sources

### CSV Format (Simple)

Expected columns: `group`, `schedule`, `enrolled`, `status`

Example:
```csv
group,schedule,enrolled,status
101,MW 10:00 AM - 11:30 AM,25/30,OK
102,MW 01:00 PM - 02:30 PM,30/30,FULL
201,TTh 09:00 AM - 10:30 AM,15/30,OK
```

**Grouping Logic**:
- First digit (course ID) = group // 100
- Groups 101, 102 → Course 1
- Group 201 → Course 2

### CSV Format (Real Data)

Expected columns: `Course Code`, `Course Name`, `Group`, `Schedule`, `Enrolled`

Example:
```csv
Course Code,Course Name,Group,Schedule,Enrolled
CIS 3100,Data Structures,1,MW 10:00 AM - 11:30 AM,25/30
CIS 3100,Data Structures,2,TTh 10:00 AM - 11:30 AM,20/30
CIS 3200,Algorithms,1,MWF 09:00 AM - 10:00 AM,30/30
```

Auto-detected by column headers. Status inferred from enrollment.

### Synthetic Generation

**Sizes**:
- `small`: 5 courses
- `medium`: 20 courses
- `large`: 50 courses

**Tightness**:
- `loose`: 3-5 sections per course
- `tight`: 2 sections per course

**Generation Parameters**:
- Day patterns: MW, TTh, MWF, T, or Th (randomly selected)
- Time slots: 8 AM to 3 PM (1-hour duration sections)
- Enrollment: 0-30 students
- Reproducibility: Use `--seed` flag for deterministic generation

### Schedule Format

Schedules are represented as strings: `"MW 10:00 AM - 11:30 AM"`

**Supported Patterns**:
- Days: M, T, W, Th (not T+h), F, S, Su
- Times: 12-hour with AM/PM (e.g., "10:00 AM", "3:45 PM")
- Ranges: `startTime - endTime`

**Examples**:
- `"MW 10:00 AM - 11:30 AM"` (Monday/Wednesday)
- `"TTh 01:00 PM - 03:00 PM"` (Tuesday/Thursday)
- `"MWF 09:00 AM - 10:00 AM"` (Monday/Wednesday/Friday)

## Verification with CP-SAT

The `--verify` flag runs both backtracking and CP-SAT solver on identical problem instances.

### What It Shows

**Comparison Table** (when both algorithms complete):
- Runtime (ms) for each algorithm
- Number of solutions found (backtracking explores multiple; CP-SAT finds optimal)
- Solver status: OPTIMAL, FEASIBLE, INFEASIBLE, UNKNOWN
- Feasibility match: green if both agree, red if conflict

### Interpreting Results

| Scenario | Meaning |
|----------|---------|
| Both FEASIBLE | Problem has valid schedules; backtracking found some, CP-SAT found optimal |
| Both INFEASIBLE | Problem has no valid solution; both algorithms agree |
| Mismatch | Potential bug; check problem data and constraint interpretation |
| CP-SAT timeout | Problem is hard; CP-SAT ran out of time before proving optimality |
| Backtracking faster | Good pruning on this problem; conflict detection is effective |
| CP-SAT faster | Problem has structure CP-SAT exploits; few variables relative to constraints |

### Time Limits

CP-SAT solver has a default timeout of 10 seconds. Override with `--verify-timeout`:

```bash
python3 main.py --generate large_tight --verify --verify-timeout 30
```

Solver may return FEASIBLE (best found) before timeout instead of OPTIMAL.

## Performance Expectations

### Backtracking Runtime

Based on problem size and constraint tightness:

| Problem | Courses | Sections | Expected Runtime | Feasible |
|---------|---------|----------|------------------|----------|
| small_loose | 5 | 15-25 | 1-5ms | 95% |
| small_tight | 5 | 10 | 2-8ms | 70% |
| medium_loose | 20 | 60-100 | 10-50ms | 80% |
| medium_tight | 20 | 40 | 50-200ms | 40% |
| large_loose | 50 | 150-250 | 100-1000ms | 60% |
| large_tight | 50 | 100 | 500-5000ms | 20% |

**Feasibility** = percentage of random problems with valid solutions.

### CP-SAT Runtime

Typically 2-10x slower than backtracking on small problems, but may be faster on structured problems. Scales poorly on large tight instances (may timeout at 10s limit).

### Memory Usage

Negligible for both algorithms on typical problem sizes (< 5MB).

## Testing Workflow

### Run All Tests

```bash
python3 -m pytest test_scheduler.py -v
```

### Test Categories

1. **Parsing Tests**: Validate schedule string parsing
   - Handles "MW 10:00 AM - 11:30 AM" format
   - Converts to minutes from midnight internally
   - Returns None for invalid input

2. **Conflict Tests**: Verify time overlap detection
   - Detects overlapping times on shared days
   - Handles non-overlapping same-day times
   - Recognizes no conflict on different days

3. **Constraint Tests**: Check viability filtering
   - Time window boundaries (earliestStart, latestEnd)
   - Full section filtering (if allowFull=False)
   - At-risk enrollment filtering (if allowAt_risk=False)

4. **Scheduling Tests**: Validate schedule generation
   - Generates valid conflict-free schedules
   - Explores multiple solutions (up to maxSchedules limit)
   - Collects accurate statistics

### Run Specific Test

```bash
python3 -m pytest test_scheduler.py::TestFunctionalEngine::test_parse_valid_mw -v
```

### Run with Coverage

```bash
python3 -m pytest test_scheduler.py --cov=scheduler --cov=core --cov=verification --cov-report=html
```

## Troubleshooting

### Issue: "ModuleNotFoundError: No module named 'ortools'"

**Solution**: Install ortools package
```bash
pip install ortools
```

### Issue: CSV File Not Found

**Solution**: Use absolute path or check relative path from current directory
```bash
python3 main.py --input /path/to/courses.csv
```

### Issue: CP-SAT Solver Timeouts on Large Problems

**Solution**: Increase timeout or use smaller dataset
```bash
python3 main.py --generate medium_loose --verify --verify-timeout 30
```

Or switch to smaller problem:
```bash
python3 main.py --generate small_loose --verify
```

### Issue: "ValueError: Missing required columns in CSV"

**Possible causes**:
1. CSV file uses different column names (use simple format: `group`, `schedule`, `enrolled`, `status`)
2. Real data format detected but missing `Course Code` column
3. Empty or malformed CSV file

**Solution**: Check column headers match expected format, or convert to simple format.

### Issue: No Schedules Found (Empty Results)

**Causes**:
1. Problem is infeasible (no valid schedule exists)
2. Constraints are too tight
3. All sections violate viability constraints

**Debugging**:
- Loosen time window: `latestEnd: "20:00"` instead of `"18:00"`
- Allow full sections: `allowFull: True`
- Check individual section times parse correctly: run test_scheduler.py
- Try synthetic data: `--generate small_loose` (95% feasible)

### Issue: Backtracking Very Slow (>10 seconds on small problem)

**Cause**: May be debugging mode or inefficient constraint specification.

**Solution**:
- Verify CSV has reasonable number of sections per course (< 20)
- Try synthetic: `--generate medium_loose` to isolate CSV parsing issue
- Check for invalid schedule formats that prevent conflict detection

## Additional Resources

### Project Documentation

- **ARCHITECTURE.md**: Complete technical documentation of all modules, data structures, and functions (grep-friendly reference)
- **CLAUDE.md**: Research vision, development principles, and variation methodology for extending the framework
- **plans/variation_1.md**: Problem statement and pseudocode for Schedule Generation (Variation 1)

### Key Concepts

**Schedule Generation (Variation 1)**:
- Input: Courses with multiple section options, time window constraints
- Output: All feasible schedules where each course has exactly one section and no time conflicts
- This is the implemented variation

**Future Variations** (planned but not yet implemented):
- Variation 2: Professor Assignment
- Variation 3: Co-Optimization (schedule + professor)
- Variation 4: Resource-Constrained (schedule + professor + rooms)

### Running Benchmarks

To create custom benchmarks:

```python
from data_gen.synthetic import generate_problem
from scheduler.scheduler_engine import generate_schedules
from data_gen.config_loader import load_config_with_defaults

# Generate problem
problem = generate_problem('medium', 'loose', seed=42)

# Setup constraints
constraints = load_config_with_defaults()

# Convert to course_sections format
course_sections = [sections for sections in problem.values()]

# Run backtracking
schedules, stats = generate_schedules(course_sections, constraints)

print(f"Found {stats['valid_schedules']} schedules in {stats['execution_time_ms']:.2f}ms")
```

### File Structure

```
timetabling-algorithms/
├── scheduler/                          # Core scheduling algorithms
│   ├── scheduler_engine.py            # Backtracking implementation (Variation 1)
│   ├── statistics.py                  # Execution metrics collection
│   └── tracing.py                     # Optional decision tracing
├── core/                              # Domain models and utilities
│   ├── models.py                      # Section, Constraints, ParsedSchedule types
│   ├── parsing.py                     # Schedule string parsing
│   └── conflict.py                    # Time overlap and viability checking
├── data_gen/                          # Data input and generation
│   ├── csv_loader.py                  # CSV file loading
│   ├── config_loader.py               # Configuration file loading
│   └── synthetic.py                   # Synthetic problem generation
├── verification/                      # CP-SAT verification module
│   └── cpsat_wrapper.py               # OR-Tools solver wrapper
├── interfaces/                        # User interfaces
│   ├── cli.py                         # Command-line mode
│   ├── tui.py                         # Interactive terminal UI
│   └── output.py                      # Result formatting
├── tests/                             # Test suites
│   ├── test_cpsat_integration.py      # CP-SAT verification tests
│   └── [additional test files]
├── test_scheduler.py                  # Unit tests for core functionality
├── main.py                            # Entry point (CLI + TUI routing)
├── README.md                          # This file
├── ARCHITECTURE.md                    # Technical implementation reference
├── CLAUDE.md                          # Research vision and methodology
└── requirements.txt                   # Python dependencies
```

## Contributing & Extending

To add new algorithm variations:

1. Create new module: `scheduler/variation_X_algorithm.py`
2. Implement generator function matching `generate_schedules()` signature
3. Add corresponding tests in `tests/test_variation_X.py`
4. Update `main.py` to register new algorithm
5. Refer to CLAUDE.md for development principles and testing strategy

## Performance Tuning

### For Faster Results

- Use synthetic generation instead of CSV (avoids I/O)
- Lower `--max-schedules` limit (stops early)
- Tighten `earliestStart` and `latestEnd` constraints
- Use `small_loose` for quick testing

### For Better Verification

- Increase `--verify-timeout` for harder problems
- Use `large_loose` to test scalability
- Save results to JSON for analysis

## License & Citation

This research framework is part of the EnrollMate course scheduling system. For integration with EnrollMate or academic citation, refer to the parent repository documentation.

---

**Last Updated**: 2026-01-28
**Current Version**: 0.1.0 (Variation 1 complete)
**Framework Status**: Active research in progress
