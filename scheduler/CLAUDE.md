# CLAUDE.md: Scheduler Implementation

This file documents the existing scheduler implementation and its connection to the research variations.

## Overview

The `scheduler/` directory contains two implementations of a **backtracking-based schedule generator**:

1. **scheduler_engine.py** (Python) - Core algorithmic engine
2. **block_scheduler.py** (Python) - Extended implementation with resource handling

## Existing Implementation: scheduler_engine.py

### Algorithm Overview

The scheduler implements a **recursive backtracking search** that generates non-overlapping course schedules:

```python
def generate_schedules(course_sections, constraints):
    # Step 1: Filter viable sections
    viable_lists = filterViable(course_sections, constraints)

    # Step 2: Backtrack through decisions
    results = []

    def backtrack(step, current_selection):
        # Base case: all courses assigned
        if step == len(viable_lists):
            results.append(createScheduleObject(current_selection, constraints))
            return

        # Recursive case: try each section for current course
        for section in viable_lists[step]:
            if not hasConflict(section, current_selection):
                backtrack(step + 1, current_selection + [section])

    backtrack(0, [])
    return results
```

### Key Components

#### 1. **ScheduleParser** (`parse_schedule_string`)
- Parses schedule strings like "MW 10:00 AM - 11:30 AM"
- Returns structure: `{days: ['M', 'W'], startTime: 600, endTime: 690}` (in minutes from midnight)
- Handles day abbreviations (M, T, W, Th, F, S, Su)

#### 2. **Section** (Dataclass)
Represents a course section with:
- `group`: section number
- `schedule`: schedule string
- `enrolled`: enrollment status (e.g., "25/30")
- `status`: enrollment status (full, at-risk, open)
- `parsed_schedule`: cached parsed result (optimization)

#### 3. **Viability Filtering**
```python
def is_viable(section, constraints):
    # Check: schedule within preferred time window?
    # Check: section not full (if allowFull=False)?
    # Check: section not at-risk (if allowAt_risk=False)?
    # Return: True if section meets all constraints
```

Used to pre-filter sections before backtracking, reducing search space.

#### 4. **Conflict Detection** (`has_conflict`)
```python
def has_conflict(section1, section2):
    # Check: do they share any days?
    # Check: do their times overlap on those days?
    # Return: True if conflict exists
```

Critical heuristic: eliminates branches early when conflicts detected.

#### 5. **Schedule Object Creation** (`create_schedule_object`)
Builds metadata about generated schedules:
- `fullCount`: number of full sections
- `endsByPreferred`: schedule ends by preferred time?
- `hasLate`: has afternoon/evening classes?
- `latestEnd`: latest class end time

Used for filtering/sorting results by quality.

### Complexity Analysis

**Time Complexity**: $O(n_1 \times n_2 \times ... \times n_c)$ where $c$ = number of courses, $n_i$ = viable sections for course $i$.

**Worst Case**: $O(2^c)$ if all sections conflict with nothing
**Typical Case**: Much faster due to conflict pruning eliminating most branches
**Best Case**: $O(c)$ if only one viable section per course

**Space Complexity**: $O(c)$ for recursion stack depth + $O(r)$ for result storage where $r$ = number of valid schedules.

### Current Limitations

1. **No heuristic ordering**: processes courses in input order (not constraint-ordered)
2. **No forward checking**: doesn't verify remaining courses still feasible
3. **No professor constraints**: can't model professor time conflicts or preferences
4. **No resource constraints**: no room allocation or capacity limits
5. **Simple filtering**: only filters by time window and enrollment status

## Extended Implementation: block_scheduler.py

(Document any extensions here once implemented)

## Connection to Research Variations

### Variation 1: Schedule Generation
This is the **baseline implementation**. The existing scheduler_engine.py implements this exact problem.

**Relationship**:
- **What's implemented**: Basic backtracking with conflict detection
- **What's missing**: Heuristic ordering (MCF, forward checking)
- **Research task**: Add heuristics to scheduler_engine.py, compare vs. CP-SAT

### Variation 2: Professor Assignment
Extends the existing approach by adding professor constraints.

**Key additions**:
- Capability filtering: professor can teach subject?
- Time overlap detection: professor teaching two conflicting sections?
- Preference scoring: which professors prefer which times?

**Reuse from Variation 1**: Conflict detection logic, filtering patterns

### Variation 3: Co-Optimization
Combines Variations 1 and 2 into a single search.

**Key additions**:
- Interleaved decisions: section selection AND professor assignment
- Shared state: which professors already assigned, to which sections
- Expanded pruning: check both schedule and professor availability

**Reuse from Variation 1-2**: All conflict detection and filtering logic

### Variation 4: Resource-Constrained
Adds room allocation and capacity limits.

**Key additions**:
- Room allocation variables
- Capacity constraints: section students <= room capacity
- Room conflict detection: room can't teach two classes simultaneously
- Load balancing: professor teaching hours

**Reuse from Variation 1-3**: All previous logic, plus new resource handling

## Heuristics to Implement

### Most-Constrained-First (MCF)

**Current implementation**: Processes courses in input order
**Improvement**: Sort courses by number of viable sections (ascending)

```python
def generateSchedulesWithMCF(course_sections, constraints):
    viable_lists = filterViable(course_sections, constraints)

    # NEW: Sort courses by constraint severity
    course_order = sorted(range(len(viable_lists)),
                         key=lambda i: len(viable_lists[i]))

    # Rest of algorithm processes courses in this order
```

**Expected impact**: Should find solutions faster by constraining hard decisions early.

### Forward Checking

**Current implementation**: None
**Improvement**: After selecting a section, verify remaining courses still have options

```python
def canExtendSchedule(section, current_schedule, remaining_viable_lists):
    new_schedule = current_schedule + [section]
    for viable_list in remaining_viable_lists:
        if not any(not hasConflict(s, new_schedule) for s in viable_list):
            return False  # Remaining course has no valid options
    return True

# In backtrack:
if canExtendSchedule(section, current_selection, remaining_viable_lists):
    backtrack(step + 1, current_selection + [section])
```

**Expected impact**: Should eliminate infeasible branches early, reducing exponential blowup.

### Section Quality Ordering

**Current implementation**: None
**Improvement**: Try "good" sections before "bad" ones within each course

```python
def sortSectionsByQuality(sections, constraints):
    return sorted(sections, key=lambda s: (
        is_full(s),           # False before True (prefer non-full)
        is_at_risk(s),        # False before True (prefer stable)
        endTime(s),           # Earlier end times preferred
        enrollmentRatio(s),   # Higher enrollment preferred
    ))

# In backtrack:
for section in sortSectionsByQuality(viable_lists[step], constraints):
    # Try sections in quality order
```

**Expected impact**: Should find high-quality solutions early, enabling pruning of worse branches.

## Testing the Scheduler

### Current Test Suite (test_scheduler.py)

Run existing tests:
```bash
python3 test_scheduler.py
```

Tests verify:
- Schedule parsing works correctly
- Conflict detection accurate
- Viability filtering functional
- Basic backtracking finds solutions

### Extending for Research

New tests needed:

1. **Heuristic Comparison**
   - Run scheduler with/without MCF heuristic
   - Measure: runtime, number of schedules found, quality scores
   - Compare: baseline vs. optimized

2. **Scalability Testing**
   - Generate test datasets of varying sizes (5, 10, 20, 50 courses)
   - Measure: runtime, memory usage, solution count
   - Plot: runtime vs. dataset size

3. **CP-SAT Benchmarking**
   - Model same input in CP-SAT
   - Run both solvers on same datasets
   - Compare: feasibility, optimality, runtime

## Performance Optimization Opportunities

1. **Caching parsed schedules** (partially done with `parsed_schedule` field)
2. **Pre-computing conflict graph** between all section pairs
3. **Parallel backtracking** (explore multiple branches simultaneously)
4. **Constraint propagation** (arc consistency preprocessing)
5. **Greedy initialization** (find one solution fast, use as baseline)

## Next Steps for Agents

1. **Understand existing code**: Read scheduler_engine.py carefully, trace through a simple example
2. **Add MCF heuristic**: Implement Most-Constrained-First ordering, measure impact
3. **Add forward checking**: Implement pruning predicate, measure impact
4. **Create CP-SAT model**: Model same problem in OR-Tools CP-SAT
5. **Benchmark**: Run experiments comparing backtracking vs. CP-SAT
6. **Document findings**: Write analysis of results and implications

## Code Quality Notes

- Uses Python type hints (TypedDict, List, Dict, Optional)
- Immutable Section dataclass (frozen=True)
- Generator pattern for scheduling (efficient memory usage)
- Caches parsed schedules for performance

## References

- Existing: scheduler_engine.py (simple backtracking baseline)
- Plans: plans/variation_1.md (research goal with pseudocode)
- Test data: sample-schedules/ directory with CSV test cases
- Benchmarks: Will be in results/ directory after implementation
