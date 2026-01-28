# CLAUDE.md - Timetabling Algorithm Research Framework

This file documents the vision, research methodology, and design philosophy behind the timetabling algorithms framework. It explains WHY the code is structured the way it is. For WHAT the code does (implementation details), see ARCHITECTURE.md. For HOW to use it, see README.md.

---

## Vision & Purpose

This repository investigates **multiple algorithmic paradigms** for solving timetabling problems, with the goal of understanding tradeoffs between **speed, optimality, and practical applicability** rather than assuming any single approach is optimal.

The project serves the **Enrollmate ecosystem** (course scheduling for students) while functioning as a **research investigation** into constraint satisfaction heuristics. We explore:
- **Backtracking with intelligent heuristics** as a fast solver
- **CP-SAT verification** to benchmark optimality and explore bounds
- **Hybrid approaches** combining speed and quality
- **Research questions**: When does each paradigm excel? Which heuristics matter most?

The implementation prioritizes **clarity, correctness, and extensibility** for research purposes.

---

## Research Methodology

### 4-Variation Progression: Problem Complexity Increasing

Rather than implementing all complexity at once, we explore timetabling through a **4-variation progression**. Each variation is a **complete research problem** with its own implementation, tests, and analysis. The goal is not to solve them sequentially, but to understand what each teaches about algorithm design.

**Variation 1: Schedule Generation** (Current - Implemented)
- Input: Subjects, section options per subject
- Constraints: Time conflicts only (hard)
- Complexity: Low
- Research question: Can fast heuristics match CP-SAT feasibility?
- Status: Backtracking + CP-SAT baseline complete (Phase 4B)

**Variation 2: Professor Assignment** (Planned)
- Input: Fixed schedules + professor availability/capabilities
- Constraints: Professor time conflicts, capability matching
- Complexity: Medium (bipartite matching)
- Research question: How much do professor preferences affect performance?

**Variation 3: Co-Optimization** (Planned)
- Input: Subjects, section options, professor capabilities
- Constraints: Generate schedules AND assign professors simultaneously
- Complexity: High (exponential in both dimensions)
- Research question: Can heuristics outperform naive CP-SAT on joint problems?

**Variation 4: Resource-Constrained Scheduling** (Future)
- Input: All of Variation 3 + room availability/capacity
- Constraints: Schedule + assignment + room allocation
- Complexity: Very high (NP-hard RCPSP variant)
- Research question: What's the practical feasibility vs. optimality tradeoff at scale?

### Algorithmic Approach

**Primary Solver**: Backtracking with intelligent heuristics
- Most-Constrained-First (MCF): Process variables with fewest options first
- Forward Checking: After assignment, verify remaining variables still solvable
- Quality Ordering: Try "good" values before "bad" ones
- Greedy Initialization: Find one solution fast, use as pruning bound

**Verification Method**: CP-SAT solver
- Encodes same problem using OR-Tools constraint solver
- Runs side-by-side with backtracking on identical test data
- Compares: feasibility, solution quality, runtime
- Benchmarks backtracking's optimality gap

**Research Goals**:
1. **Feasibility**: Do heuristics find valid solutions?
2. **Optimality**: How close to CP-SAT's optimal?
3. **Scalability**: Where does each approach break down?
4. **Heuristic Impact**: Which heuristics matter most?
5. **Practical Guidance**: When should practitioners use each approach?

---

## Architectural Philosophy

### Core Principle: Clean Domain Separation

The codebase separates concerns into **7 feature domains** (see ARCHITECTURE.md for implementation details):

1. **Core Domain Models** - Immutable data structures, parsing, validation
2. **Conflict Detection** - Time overlap checking, viability filtering
3. **Scheduling Engine** - Backtracking algorithm with statistics collection
4. **Data Generation** - CSV loading, synthetic problem generation
5. **CP-SAT Verification** - OR-Tools solver integration
6. **Interfaces** - CLI and TUI for execution
7. **Testing** - Unit tests for correctness

**Why this separation?**
- Enables independent testing of each domain
- Makes adding heuristics straightforward (only changes scheduling engine)
- Allows variations 2-4 to reuse core parsing and conflict detection
- Clear dependency graph prevents accidental coupling

### Parse-or-None Error Handling

Parsing functions return `None` on invalid input rather than raising exceptions:

```python
parsed = parse_schedule_string(user_input)
if parsed is None:
    # handle invalid input gracefully
```

**Why?** Schedule strings come from human data entry (CSV, web forms). Raising exceptions would crash the scheduler; returning `None` lets us gracefully filter invalid sections.

### Immutable Data Structures

Section objects are frozen dataclasses:

```python
@dataclass(frozen=True)
class Section:
    group: int
    schedule: str
    enrolled: str
    status: str
    parsed_schedule: Optional[ParsedSchedule] = None
```

**Why immutable?**
- Prevents accidental mutation during backtracking recursion
- Makes caching safe (parsed_schedule field can be mutated during creation, then frozen)
- Enables structural equality for testing
- Signals intent: sections are fixed problem data, not mutable state

### Caching Strategy

Two levels of caching minimize redundant parsing:

**Level 1: Section-level caching**
- `Section.parsed_schedule` stores first parse result
- Eliminates re-parsing identical schedules

**Level 2: Pre-filtering**
- Viability filtering happens once before backtracking
- Removes sections violating constraints
- All conflict checks then work only on viable sections

**Why?** Schedule parsing involves regex + time format conversion. For typical problems (5-50 courses), this is called 10-250+ times. Caching reduces parsing overhead by 90%.

### Time Format Unification

All times stored internally as **minutes from midnight** (0-1440):

- `10:00 AM` → 600 minutes
- `11:30 AM` → 690 minutes
- `2:30 PM` → 870 minutes

**Why?** Makes overlap detection trivial:
```python
return start_a < end_b and end_a > start_b
```

No need for date objects, timezone handling, or complex comparisons.

### Constraints as TypedDict

Scheduling constraints are defined as a TypedDict:

```python
class Constraints(TypedDict):
    earliestStart: str        # "08:00" (HH:MM format)
    latestEnd: str            # "18:00"
    allowFull: bool           # Include full sections?
    allowAt_risk: bool        # Include at-risk sections?
    maxSchedules: int         # Max schedules to generate
    maxFullPerSchedule: int   # Max full sections per valid schedule
```

**Why TypedDict over class?**
- Type-safe (mypy validates usage)
- No runtime overhead (not a real class, just dict)
- Matches database schema naming (snake_case)
- Easy to serialize/deserialize from YAML/JSON

**Hard vs Soft Constraints:**
- **Hard constraints** (must satisfy): time conflicts, enrollment filtering, time window
- **Soft constraints** (prefer to satisfy): minimal full sections, ends by preferred time
- Current implementation enforces hard, collects soft as metadata for later ranking

---

## Design Decisions

### Why Backtracking First?

1. **Speed**: Can find multiple solutions in 1-100ms for realistic problems (see ARCHITECTURE.md performance table)
2. **Multiple Solutions**: Explores solution space broadly, finds diverse schedules
3. **Exploration**: Good testbed for measuring heuristic impact
4. **Simplicity**: Core algorithm is recursive (easy to understand and extend)

Constraint Satisfaction Problems (CSPs) have exponential worst case, but real course scheduling is often tight (few valid solutions). Backtracking can be fast with good pruning.

### Why CP-SAT Verification?

1. **Optimality**: Proves when backtracking is optimal vs. suboptimal
2. **Feasibility Validation**: Confirms if problem is actually infeasible
3. **Benchmarking**: Measures heuristic impact quantitatively
4. **Industrial Solver**: OR-Tools CP-SAT is production-grade, trusted

We don't use CP-SAT for scheduling (slower, can't find multiple solutions easily). We use it to understand where backtracking wins and loses.

### Why These Data Structures?

**ParsedSchedule**: `{days: List[str], startTime: int, endTime: int}`
- Days as list (not bitmask) for clarity
- Time as int minutes for simple comparisons
- Cached on Section to avoid re-parsing

**Section as frozen dataclass**
- Immutability prevents bugs in backtracking
- Dataclass provides __repr__ and __eq__ for testing
- Frozen means parsed_schedule caching is thread-safe

**GeneratedSchedule**: `{selections: List[Section], parsed: List[ParsedSchedule], meta: ScheduleMeta}`
- Separates input (selections) from derived (parsed, meta)
- Parsed array allows schedule rendering without re-parsing
- Meta enables result ranking and filtering

**Statistics as class with increment methods**
- Simpler than dict updates scattered in backtracking
- Enables future extensions (e.g., detailed heuristic metrics)

### Why No Heuristics Yet?

Current implementation is **baseline backtracking only** (no MCF, forward checking, etc.) because:

1. **Research-First**: Want to measure heuristic impact against known baseline
2. **Clarity**: Simpler code easier to understand and extend
3. **Phase 1 Complete**: Schedule generation works; time to add heuristics incrementally
4. **Measurement Protocol**: Each heuristic gets tested separately to quantify its contribution

Adding all heuristics at once would be fast but wouldn't reveal which ones matter.

---

## Critical Context

### Timetabling Problem Space

**NP-hard constraint satisfaction**. The problem is to select one section per course such that:
- No two selected sections have time conflicts (hard constraint)
- Sections satisfy time window, enrollment, and capacity filters (hard constraints)
- (Future) Minimize number of full sections, end time, etc. (soft constraints)

Number of possible assignments: `n₁ × n₂ × ... × nₖ` where nᵢ = number of sections for course i.

For 5 courses with 3 sections each: 3⁵ = 243 combinations (manageable with pruning).
For 50 courses with 3 sections each: 3⁵⁰ ≈ 5×10²³ (requires strong heuristics).

### Schedule Format Parsing

Human-entered schedule strings are fragile:
- `"MW 10:00 AM - 11:30 AM"` (standard)
- `"MW 10:00am-11:30am"` (missing spaces)
- `"M,W 10:00 AM - 11:30 AM"` (comma separator)
- `"10:00 AM - 11:30 AM MW"` (days at end)
- Invalid formats that should be filtered

**Solution**: Regex-based parser with case insensitivity and robust error handling. Returns `None` for invalid input (never crashes).

**Edge Cases**:
- `"12:00 AM"` = midnight (0 minutes)
- `"12:00 PM"` = noon (720 minutes)
- `"12:30 AM"` = 30 minutes past midnight
- Adjacent times: `"10:00-11:30"` and `"11:30-1:00"` do NOT conflict

### Constraint Categories

**Hard Constraints** (violation = infeasible schedule):
- Exactly one section per course
- No time overlaps between selected sections
- Section start time >= earliestStart constraint
- Section end time <= latestEnd constraint
- (If allowFull=False) Section must not be full
- (If allowAt_risk=False) Section must not be at-risk

**Soft Constraints** (current implementation collects as metadata):
- Minimize number of full sections
- End time <= preferred end time
- Avoid afternoon/evening classes

Current backtracking doesn't optimize soft constraints, just finds feasible solutions and metadata.

---

## Development Principles

### For Implementing Features

**Order of Implementation**:
1. **Core domain models** - Define data structures and parsing
2. **Constraint/conflict checking** - Implement validation logic
3. **Algorithm** - Implement scheduling logic
4. **Tests** - Write unit tests before integration
5. **Documentation** - Document design decisions and tradeoffs

**Testing Strategy**:
- **Correctness tests**: Verify parsing, conflict detection, scheduling produce expected results
- **Feasibility tests**: Compare backtracking output against known feasible/infeasible problems
- **Scalability tests**: Measure runtime across small/medium/large problem sizes
- **Optimality tests**: Compare against CP-SAT optimal (once implemented)
- **Heuristic impact tests**: Measure each heuristic's contribution separately

### For Extending to Variations

**Variation 2: Professor Assignment**
1. Keep core parsing/conflict from Variation 1
2. Add professor dataclass and capability checking
3. Implement professor assignment backtracking (after schedule selection)
4. Add tests and CP-SAT verification for professor assignment
5. Document professor matching algorithm

**Variation 3: Co-Optimization**
1. Combine schedule and professor variable ordering
2. Test different constraint processing orders
3. Measure heuristic impact on joint problem
4. Compare to sequential approach (Variation 1 + 2)

**Variation 4: Resource-Constrained**
1. Add room dataclass and capacity constraints
2. Extend backtracking to handle room allocation
3. Implement room conflict detection (no overbooking)
4. Test at realistic university scale

### For Measuring Success

**Correctness**:
- All solutions satisfy hard constraints (no overlaps, feasibility)
- Solutions match manual spot-checks

**Comprehensiveness**:
- Backtracking explores solution space broadly
- Finds multiple diverse solutions (not just first)

**Comparison Rigor**:
- Backtracking vs. CP-SAT benchmarked on identical datasets
- Feasibility always matches (or we found a bug)

**Heuristic Impact Clarity**:
- Each heuristic's contribution measured separately
- Baseline (no heuristics) → +MCF → +FC → +QO, etc.
- Document runtime and quality impact of each

**Scalability Analysis**:
- Clear understanding of where each algorithm breaks
- Performance envelope documented (ARCHITECTURE.md)

---

## Common Gotchas

### Schedule Parsing is Fragile

**Problem**: Schedule format is human-entered, inconsistent case/spacing.

**Symptoms**:
- Parser returns `None` for valid-looking input
- Sections silently dropped during filtering
- Silent failures in backtracking

**Solution**:
- Use regex with `re.IGNORECASE` and flexible whitespace
- Handle 24-hour and 12-hour time formats
- Cache parsed results in Section dataclass
- Test with messy real-world data (not just clean examples)

### Time Overlap Detection Has Edge Cases

**Problem**: Does "10:00 AM - 11:30 AM" conflict with "11:30 AM - 1:00 PM"?

**Answer**: No (they don't overlap, adjacent times are OK).

**Gotcha**: Off-by-one errors in time comparisons.

**Correct Implementation**:
```python
def times_overlap(start_a, end_a, start_b, end_b):
    return start_a < end_b and end_a > start_b  # NOT <=
```

**Wrong** (would incorrectly detect conflict on adjacent times):
```python
return start_a <= end_b and end_a >= start_b  # BUG
```

### Backtracking Explosion on Large Problems

**Problem**: Without heuristics, naive backtracking explores O(n₁ × n₂ × ... × nₖ) branches.

**Symptom**: 50+ courses takes minutes instead of milliseconds.

**Solution**:
- MCF ordering reduces branching by 10-100x
- Forward checking catches dead-ends early
- Set `maxSchedules` to stop after N solutions (don't explore entire space)
- Pre-filter viability to shrink search space

### Variation Boundaries Blur Easily

**Problem**: Variation 3 accidentally becomes Variation 4 during implementation (added professor logic without realizing room logic was needed).

**Solution**:
- Each variation is independent (don't inherit from previous)
- Clearly separate concerns (schedule generation vs. professor assignment)
- Test Variation 2 in isolation before attempting Variation 3
- Document constraint assumptions for each variation

### Frozen Dataclass Immutability is Strict

**Problem**: Trying to mutate Section after creation fails silently or with cryptic errors.

**Symptom**:
```python
section = Section(1, "MW 10:00 AM - 11:30 AM", "15/30", "OK")
section.status = "FULL"  # FrozenInstanceError!
```

**Solution**: Create new objects during preprocessing, not in backtracking:
```python
# Right: Preprocess once
sections = [Section(...) for row in csv]

# Wrong: Trying to mutate in backtracking
# (Would need unfrozen Section, loses safety benefits)
```

---

## Success Metrics

### What "Good" Looks Like

1. **Correctness**: All solutions satisfy hard constraints (no overlaps, feasibility)
2. **Comprehensiveness**: Backtracking explores solution space broadly (multiple solutions)
3. **Comparison Rigor**: Backtracking vs. CP-SAT benchmarked on identical datasets
4. **Heuristic Impact Clarity**: Each heuristic's contribution measured and documented
5. **Scalability Analysis**: Clear understanding of where each algorithm breaks down
6. **Research Insights**: Published findings about when to use each approach

### Performance Envelope (From ARCHITECTURE.md)

| Problem Size | Courses | Sections | BT Time | CP-SAT Time | Feasible |
|--------------|---------|----------|---------|------------|----------|
| small_loose | 5 | 15-25 | 1-5ms | 10-50ms | 95% |
| small_tight | 5 | 10 | 2-8ms | 5-20ms | 70% |
| medium_loose | 20 | 60-100 | 10-50ms | 100-500ms | 80% |
| medium_tight | 20 | 40 | 50-200ms | 200-800ms | 40% |
| large_loose | 50 | 150-250 | 100-1000ms | 1-10s | 60% |
| large_tight | 50 | 100 | 500-5000ms | 5-60s | 20% |

### Extension Readiness

- Can Variations 2-4 be implemented? (Core parsing/conflict reusable)
- Can heuristics be added without refactoring? (Clean algorithm interface)
- Can new solvers be plugged in? (Verification infrastructure ready)

---

## Project Structure Overview

The codebase is organized into **7 feature domains** (see ARCHITECTURE.md for complete breakdown):

1. **core/models.py** - ParsedSchedule, Section, Constraints, GeneratedSchedule types
2. **core/parsing.py** - Schedule string parsing (times, days, formats)
3. **core/conflict.py** - Time overlap, viability, enrollment filtering
4. **scheduler/scheduler_engine.py** - Main backtracking algorithm
5. **scheduler/statistics.py** - Metrics collection
6. **scheduler/tracing.py** - Optional debug tracing
7. **data_gen/** - CSV loading, synthetic generation, config handling
8. **verification/cpsat_wrapper.py** - OR-Tools verification
9. **interfaces/cli.py** - Command-line interface
10. **interfaces/tui.py** - Interactive terminal interface
11. **test_scheduler.py** - Unit tests
12. **main.py** - Entry point

**For Research**:
- `main.py --algo backtracking_v1 --generate medium_loose --verify` - Test algorithm
- `test_scheduler.py` - Run tests
- `results/variation_1_benchmark.json` - Capture measurements

**For Extension**:
- `scheduler/scheduler_engine.py` - Modify core algorithm
- `core/conflict.py` - Add new constraint types
- `tests/test_*.py` - Add test cases
- `verification/cpsat_wrapper.py` - Add optimization objective

**For Integration**:
- `data_gen/csv_loader.py` - Load real CSV data
- `interfaces/cli.py` - Command-line interface
- `interfaces/tui.py` - Interactive terminal interface

---

## Connection to Broader Research

This project sits at the intersection of:

1. **Constraint Satisfaction**: CSP solving techniques (backtracking, forward checking, arc consistency)
2. **Combinatorial Optimization**: NP-hard problem solving with heuristics
3. **Educational Scheduling**: Specific to course timetabling domain
4. **Practical Engineering**: Production-grade solver selection for real applications

Research findings will contribute to understanding when heuristics outperform solvers and which algorithmic choices matter most for practical scheduling problems.

---

## Notes on Phase 4B Status

**Phase 4B Complete** (as of latest git log):
- Core Variation 1 (schedule generation) fully implemented
- Backtracking baseline + statistics collection working
- CP-SAT verification infrastructure in place
- CLI and TUI interfaces functional
- Test suite covers parsing, conflict detection, scheduling

**Ready for Phase 5** (Heuristic Optimization):
- Add MCF ordering → measure impact
- Add forward checking → measure impact
- Test heuristic combinations
- Benchmark against CP-SAT
- Document findings

**Future Phases** (Variations 2-4):
- Variation 2: Professor assignment (bipartite matching)
- Variation 3: Co-optimization (schedule + professor)
- Variation 4: Resource constraints (schedule + professor + rooms)

---

**Last Updated**: 2026-01-28
**Status**: Phase 4B Complete - Ready for Heuristic Research
**Philosophy Alignment**: SCALPEL (research project with clear documentation and measurement)
