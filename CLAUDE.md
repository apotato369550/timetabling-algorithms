# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## Vision & Purpose

This repository investigates **multiple algorithmic paradigms** for solving timetabling problems, with the goal of understanding tradeoffs between **speed, optimality, and practical applicability**.

Rather than assuming any single approach is optimal, we explore:
- **Backtracking with intelligent heuristics** as the primary solver (fast, finds multiple feasible solutions)
- **CP-SAT verification** to benchmark optimality and explore bounds
- **Hybrid approaches** combining speed and quality
- **Research questions** about when each paradigm excels

The project serves the **Enrollmate ecosystem** (course scheduling for students) while functioning as a **research investigation** into constraint satisfaction heuristics.

---

## Architectural Philosophy

### Core Principle: Progressive Problem Complexity

The project uses a **4-variation progression** to investigate timetabling at increasing complexity levels:

1. **Variation 1: Schedule Generation** - Simplest (no professor/resource constraints)
2. **Variation 2: Professor Assignment** - Medium (bipartite matching)
3. **Variation 3: Co-Optimization** - Hard (schedule + professor simultaneous)
4. **Variation 4: Resource-Constrained** - Hardest (schedule + professor + rooms)

Each variation is a **complete research problem** with its own implementation, tests, benchmarks, and analysis. The goal is not to solve them sequentially, but to understand what each teaches about algorithm design.

### Backtracking as First-Class Algorithm

This project treats **backtracking with heuristics** as an equal peer to **CP-SAT**, not a fallback. The comparison explores:
- **Feasibility**: Can heuristics find valid solutions?
- **Optimality**: How close to CP-SAT's optimal?
- **Scalability**: Where does each approach break?
- **Practical Utility**: When should practitioners use backtracking vs. CP-SAT?

### Core Architecture Pattern

```
Problem Definition (variation_X.md)
    ↓
Backtracking Implementation (scheduler/XX_algorithm.py)
    ↓ [Add Heuristics]
    ↓
CP-SAT Verification Model (scheduler/XX_cpsat.py)
    ↓ [Run side-by-side]
    ↓
Benchmark Suite (tests/test_variation_X.py)
    ↓ [Runtime, quality, scalability]
    ↓
Analysis Report (results/variation_X_analysis.md)
```

---

## Critical Context

### Problem Domain

**Timetabling problems** are NP-hard constraint satisfaction problems. This project focuses on **block section scheduling**:
- Input: Subjects (courses), section options per subject, professor capabilities, room constraints
- Output: Feasible assignments that satisfy hard constraints (no time overlaps, capability matching) and optimize soft constraints (quality metrics)

### Key Terminology

- **Subject/Course**: A course a student must take (e.g., "Math 101")
- **Section**: A specific offering of a subject with time/professor/room (e.g., "Math 101 - Section A - MW 10-11:30AM")
- **Block**: A group of subjects that must be scheduled together (e.g., all courses in Year 1 of a degree)
- **Constraint**: Hard (must satisfy) vs. Soft (prefer to satisfy)
- **Conflict**: Two sections overlap in time or share incompatible resources

### Data Representations

**Schedule String Format**: "MW 10:00 AM - 11:30 AM"
- Days: M, T, W, Th, F, S, Su (e.g., "MW", "TTh", "MWF")
- Times: HH:MM AM/PM → converted internally to minutes from midnight
- Parser: `parse_schedule_string()` returns `{days: ['M', 'W'], startTime: 600, endTime: 690}`

**Enrollment Status**:
- "FULL" or "OK" (string field in Section dataclass)
- Derived properties: `is_full()`, `is_at_risk()` for filtering

**Constraints Dictionary** (`Constraints` TypedDict):
```
{
    'earliestStart': '08:00',    # Don't schedule before this
    'latestEnd': '18:00',        # Don't schedule after this
    'allowFull': False,          # Skip full sections?
    'allowAt_risk': True,        # Allow enrollment-at-risk?
    'maxSchedules': 5,           # Stop after finding N schedules
    'maxFullPerSchedule': 0      # Max full sections per schedule
}
```

---

## Development Principles

### 1. Understand Before Implementing

For each variation:
1. Read `plans/variation_X.md` → understand the problem statement and pseudocode
2. Review `scheduler/CLAUDE.md` → understand existing backtracking patterns
3. Trace through test data manually → verify understanding of algorithm flow

### 2. Backtracking First, Heuristics Second

For each variation, implement in this order:
1. **Basic backtracking** (naive recursive search, no heuristics)
2. **Verify correctness** (tests pass, output makes sense)
3. **Add heuristics incrementally** (MCF, then forward checking, then others)
4. **Measure impact** (runtime, solution count, quality) for each heuristic added

### 3. Heuristics to Explore

Core heuristics implemented across variations:

| Heuristic | What It Does | When to Use |
|-----------|-------------|-----------|
| **Most-Constrained-First (MCF)** | Process variables with fewest options first | Every variation (baseline improvement) |
| **Forward Checking** | After assignment, verify remaining variables still solvable | Medium+ complexity (catches dead-ends early) |
| **Quality Ordering** | Try "good" values before "bad" ones | All variations (finds high-quality solutions early) |
| **Arc Consistency** | Pre-process to eliminate impossible value combinations | Variation 3+ (expensive but payoff high) |
| **Greedy Initialization** | Find one solution fast, use as pruning bound | Hard variations (provides baseline) |

### 4. CP-SAT as Verification Tool

For each variation, after implementing backtracking:
1. Encode the **same problem** in CP-SAT using OR-Tools `CpModel`
2. Run both algorithms on identical test data
3. Compare: feasibility, solution quality (if optimization objective), runtime
4. Document: where backtracking wins, where CP-SAT wins, why

### 5. Testing Strategy

Each variation needs:

```
tests/test_variation_X.py
├── Correctness Tests
│   ├── Parsing (schedule strings parse correctly)
│   ├── Conflict Detection (has_conflict() is accurate)
│   └── Constraints (viable filtering works)
├── Feasibility Tests
│   ├── Known Feasible: verify both algorithms find solution
│   ├── Known Infeasible: verify both correctly reject
│   └── Solution Validation: all solutions satisfy constraints
├── Scalability Tests
│   ├── Small: 5-10 subjects, <1s expected runtime
│   ├── Medium: 20-30 subjects, <10s expected runtime
│   └── Large: 50+ subjects, measure scaling behavior
└── Optimality Tests
    ├── Compare to CP-SAT optimal
    ├── Measure quality gaps across heuristic variants
    └── Analyze when heuristics matter most
```

### 6. Measurement Protocol

For each experiment, capture:
- **Runtime**: milliseconds (use `time.perf_counter()`)
- **Solution Quality**: objective score (if optimizing) or custom metrics
- **Solution Count**: number of feasible solutions found
- **Optimality Gap**: (CP-SAT optimal - backtracking best) / CP-SAT optimal
- **Heuristic Impact**: runtime/quality change from adding each heuristic

Document in `/results/variation_X_benchmark.json`:
```json
{
  "variation": 1,
  "dataset": "small_test_5_subjects",
  "algorithms": {
    "backtracking_naive": {"runtime_ms": 15, "solutions": 3, "quality_score": 95},
    "backtracking_mcf": {"runtime_ms": 8, "solutions": 3, "quality_score": 97},
    "backtracking_mcf_fc": {"runtime_ms": 4, "solutions": 3, "quality_score": 98},
    "cpsat": {"runtime_ms": 120, "solutions": 1, "quality_score": 100, "optimal": true}
  }
}
```

---

## Common Gotchas

### 1. Schedule String Parsing is Fragile

**Problem**: Schedule format is human-entered, inconsistent case/spacing.

**Solution**:
- Use regex with `re.IGNORECASE`
- Handle 24-hour and 12-hour time formats
- Cache parsed results in Section dataclass (`parsed_schedule` field)
- Test with messy real-world data (see `test_scheduler.py` for examples)

### 2. Time Overlap Detection Has Edge Cases

**Problem**: Does "10:00 AM - 11:30 AM" conflict with "11:30 AM - 1:00 PM"?

**Answer**: No (they don't overlap, adjacent times are OK).

**Implementation**: Use `startTime < other.endTime and endTime > other.startTime`

### 3. Backtracking Explosion on Large Problems

**Problem**: Without heuristics, naive backtracking explores $O(n_1 \times n_2 \times ... \times n_s)$ branches.

**Solution**:
- MCF ordering reduces branching by 10-100x
- Forward checking catches dead-ends early
- Set `maxSchedules` to stop after N solutions (don't explore entire space)

### 4. CP-SAT Timeout on Hard Problems

**Problem**: Variation 3-4 may timeout on large instances.

**Solution**:
- Set time limit: `solver.parameters.max_time_in_seconds = 10`
- Use heuristic search: `solver.parameters.log_search_progress = False`
- Compare "best found" vs. "optimal" status

### 5. Heuristic Ordering Matters More Than Expected

**Problem**: Different constraint orderings produce vastly different runtimes.

**Solution**:
- Test multiple heuristic combinations
- Measure each heuristic in isolation (add one at a time)
- Don't assume MCF alone is sufficient

### 6. Variation Boundaries Blur Easily

**Problem**: Variation 3 accidentally becomes Variation 4 during implementation.

**Solution**:
- Each variation is independent (don't inherit from previous)
- Clearly separate concerns (schedule generation vs. professor assignment)
- Test Variation 2 in isolation before attempting Variation 3

---

## Project Structure

```
timetabling-algorithms/
├── scheduler/                          # Core implementations
│   ├── scheduler_engine.py            # Variation 1: Backtracking (baseline)
│   ├── block_scheduler.py             # Extended scheduler (planning)
│   ├── statistics.py                  # Statistics collection
│   ├── tracing.py                     # Debug tracing
│   ├── config_loader.py               # Configuration handling
│   ├── csv_loader.py                  # CSV input parsing
│   └── CLAUDE.md                      # Scheduler implementation details
├── tests/                              # Test suites
│   ├── test_scheduler.py              # Tests for scheduler_engine.py (Variation 1)
│   ├── test_variation_2.py            # Tests for Variation 2 (professor assignment)
│   ├── test_variation_3.py            # Tests for Variation 3 (co-optimization)
│   └── test_variation_4.py            # Tests for Variation 4 (resource-constrained)
├── plans/                              # Research scaffolding
│   ├── context.md                     # Research vision and framework
│   ├── CLAUDE.md                      # Variation methodology
│   ├── variation_1.md                 # Variation 1 problem + pseudocode
│   ├── variation_2.md                 # Variation 2 problem + pseudocode
│   ├── variation_3.md                 # Variation 3 problem + pseudocode
│   └── variation_4.md                 # Variation 4 problem + pseudocode
├── results/                            # Benchmarks and analysis (post-implementation)
│   ├── variation_1_benchmark.json     # Runtime/quality measurements
│   ├── variation_1_analysis.md        # Findings and insights
│   └── [similar for variations 2-4]
├── data/                               # Sample datasets
│   ├── config_example.yaml            # Example config file
│   └── [CSV test data]
├── docs/                               # Supporting documentation
│   └── sessions/                      # Session logs and exploration notes
├── scheduler_cli.py                   # CLI tool for manual testing
├── test_scheduler.py                  # Test runner (Variation 1)
├── README.md                          # User manual
├── RESEARCH_INDEX.md                  # Index of research findings
├── COMPLETION_REPORT.md               # Project status report
└── .git/                              # Version control
```

### Key Files for Agents

- **Problem Understanding**: `plans/variation_X.md` (problem statement + pseudocode)
- **Implementation Patterns**: `scheduler/CLAUDE.md` + `scheduler/scheduler_engine.py` (baseline backtracking)
- **Testing Strategy**: `test_scheduler.py` (example test patterns)
- **Execution**: `scheduler_cli.py` (manual testing interface)

---

## Success Metrics

### What "Good" Looks Like

1. **Correctness**: All solutions satisfy hard constraints (no overlaps, feasibility)
2. **Comprehensiveness**: Backtracking explores solution space broadly (multiple solutions)
3. **Comparison Rigor**: Backtracking vs. CP-SAT benchmarked on identical datasets
4. **Heuristic Impact Clarity**: Each heuristic's contribution measured and documented
5. **Scalability Analysis**: Clear understanding of where each algorithm breaks down
6. **Research Insights**: Published findings about when to use each approach

### Bad Signs

- ❌ Only running backtracking without CP-SAT verification
- ❌ Heuristics added without measuring impact separately
- ❌ Test data all small (need scalability tests too)
- ❌ No documentation of design decisions
- ❌ Mixing variation implementations (Variation 2 accidentally includes room constraints)

---

## Development Workflow

### Step 1: Choose a Variation

Pick one variation (e.g., Variation 2: Professor Assignment).

### Step 2: Understand the Problem

1. Read `plans/variation_2.md` thoroughly
2. Review `plans/context.md` for methodology
3. Trace through pseudocode manually
4. Ask questions if unclear

### Step 3: Implement Backtracking (Naive)

1. Create `scheduler/variation_2_algorithm.py`
2. Implement basic backtracking (no heuristics yet)
3. Add unit tests in `tests/test_variation_2.py`
4. Verify correctness on small datasets

### Step 4: Add Heuristics Incrementally

1. Implement MCF ordering (measure impact)
2. Implement Forward Checking (measure impact)
3. Try a third heuristic if beneficial
4. Document which heuristics matter most

### Step 5: Implement CP-SAT Verification

1. Create `scheduler/variation_2_cpsat.py`
2. Model same problem in OR-Tools
3. Run both algorithms on identical test sets
4. Compare: feasibility, quality, runtime

### Step 6: Benchmark & Analyze

1. Create comprehensive test datasets (small, medium, large)
2. Run all algorithms across all datasets
3. Capture results in `results/variation_2_benchmark.json`
4. Write analysis in `results/variation_2_analysis.md`

### Step 7: Document Findings

Update `RESEARCH_INDEX.md` and `COMPLETION_REPORT.md` with:
- What we learned
- When to use backtracking vs. CP-SAT
- What heuristics matter most
- Insights for next variation

---

## Commonly Used Commands

### Running Tests
```bash
# Run all tests
python3 -m pytest tests/ -v

# Run specific variation tests
python3 -m pytest tests/test_variation_1.py -v

# Run single test
python3 -m pytest tests/test_variation_1.py::TestClass::test_name -v

# Run with coverage
python3 -m pytest tests/ --cov=scheduler --cov-report=html
```

### CLI Tool
```bash
# Interactive menu for manual testing
python3 scheduler_cli.py

# Standard scheduler (Variation 1 demo)
python3 -c "from scheduler_cli import run_standard_scheduler; run_standard_scheduler()"

# Block scheduler (Variation 2+ testing)
python3 -c "from scheduler_cli import run_block_scheduler; run_block_scheduler()"
```

### Linting & Type Checking
```bash
# Check type hints
python3 -m mypy scheduler/ --ignore-missing-imports

# Format code
python3 -m black scheduler/ tests/ scheduler_cli.py

# Lint
python3 -m pylint scheduler/ --disable=all --enable=E,F
```

### Running Individual Variation Implementations
```bash
# After implementing scheduler/variation_2_algorithm.py:
python3 -c "from scheduler.variation_2_algorithm import *; print(generate_professor_schedules(...))"

# After implementing scheduler/variation_2_cpsat.py:
python3 -c "from scheduler.variation_2_cpsat import *; print(cpsat_schedule_assignment(...))"
```

---

## Notes on Architecture Refactoring

You mentioned this codebase is "due for a massive refactor." Key considerations:

1. **Keep Variation Separation Clean**: Each variation should be independent. Use separate modules, not inheritance.

2. **Heuristics Library**: Consider a reusable heuristics abstraction (MCF, forward checking) if implementing Variations 2-4.

3. **Testing Framework**: Current test structure works well; scale it up for multiple variations.

4. **Benchmarking**: Add a dedicated `benchmarks/` module with standardized measurement protocol.

5. **CLI Tool**: `scheduler_cli.py` could evolve into a test runner for all variations.

For now, prioritize **clarity and research rigor** over architectural perfection. Refactoring becomes worth it once you understand the full scope (all 4 variations).

---

**Last Updated**: 2026-01-23
**Philosophy Alignment**: Scalpel (research project with clear documentation and measurement)
**Reference**: `/home/jay/.claude/agents/philosophy/SCALPEL_PHILOSOPHY.md`
