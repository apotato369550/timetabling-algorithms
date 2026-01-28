# Architecture Documentation: Timetabling Algorithm Research Framework

This document describes the actual implementation of the timetabling algorithm research framework, providing a grep-friendly source-of-truth for how services, functions, and endpoints work together.

---

## Table of Contents

1. [Feature Domain 1: Core Domain Models and Parsing](#feature-domain-1-core-domain-models-and-parsing)
2. [Feature Domain 2: Conflict Detection and Constraint Checking](#feature-domain-2-conflict-detection-and-constraint-checking)
3. [Feature Domain 3: Scheduling Engine (Variation 1 - Backtracking)](#feature-domain-3-scheduling-engine-variation-1---backtracking)
4. [Feature Domain 4: Data Generation and Input Loading](#feature-domain-4-data-generation-and-input-loading)
5. [Feature Domain 5: CP-SAT Verification](#feature-domain-5-cp-sat-verification)
6. [Feature Domain 6: Interfaces (CLI and TUI)](#feature-domain-6-interfaces-cli-and-tui)
7. [Feature Domain 7: Testing Architecture](#feature-domain-7-testing-architecture)
8. [Cross-Feature Dependencies](#cross-feature-dependencies)
9. [Grep-Friendly Index](#grep-friendly-index)
10. [Performance Characteristics](#performance-characteristics)

---

## Feature Domain 1: Core Domain Models and Parsing

### Pattern Overview

```
Raw Schedule String "MW 10:00 AM - 11:30 AM"
    ↓
parse_schedule_string() [core/parsing.py]
    ↓
ParsedSchedule {days: ['M', 'W'], startTime: 600, endTime: 690}
    ↓
Section (dataclass) with cached parsed_schedule
    ↓
Used by conflict detection and scheduling algorithms
```

Core domain encapsulates:
- **ParsedSchedule**: Type-safe representation of time/day scheduling
- **Section**: Immutable dataclass representing a course section
- **Constraints**: TypedDict defining scheduling boundaries and preferences
- **Parsing functions**: Robust schedule string parsing with error handling

---

### Module: core/models.py

**Purpose**: Defines data structures for the entire scheduling framework.

**Data Structures**:

```python
class ParsedSchedule(TypedDict):
    days: List[str]           # ['M', 'W', 'Th', etc.]
    startTime: int            # Minutes from midnight (0-1440)
    endTime: int              # Minutes from midnight (0-1440)

@dataclass(frozen=True)
class Section:
    group: int                # Section number/identifier
    schedule: str             # "MW 10:00 AM - 11:30 AM" (raw string)
    enrolled: str             # "25/30" (current/total enrollment)
    status: str               # "OK", "FULL", "AT-RISK"
    parsed_schedule: Optional[ParsedSchedule] = None  # Cached parse result

class Constraints(TypedDict):
    earliestStart: str        # "08:00" (HH:MM format)
    latestEnd: str            # "18:00" (HH:MM format)
    allowFull: bool           # Include full sections?
    allowAt_risk: bool        # Include at-risk sections?
    maxSchedules: int         # Max schedules to generate
    maxFullPerSchedule: int   # Max full sections per valid schedule

class ScheduleMeta(TypedDict):
    fullCount: int            # Number of full sections in schedule
    endsByPreferred: bool     # Latest end time <= preferred end?
    hasLate: bool             # Has afternoon/evening (>= 12:00) classes?
    latestEnd: int            # Latest class end time in minutes

class GeneratedSchedule(TypedDict):
    selections: List[Section] # Selected sections forming valid schedule
    parsed: List[ParsedSchedule]  # Parsed schedules for selected sections
    meta: ScheduleMeta        # Quality metadata for schedule
```

**Key Properties**:
- `Section` is immutable (frozen=True) to prevent accidental mutations
- `ParsedSchedule` stores times in **minutes from midnight** (0 = 00:00, 1440 = 24:00)
- `parsed_schedule` field on Section enables caching to avoid re-parsing
- `Constraints` includes both hard (feasibility) and soft (quality) constraints

**Used By**:
- All scheduling algorithms (scheduler/scheduler_engine.py)
- Conflict detection (core/conflict.py)
- Input loading (data_gen/csv_loader.py, data_gen/config_loader.py)
- Verification (verification/cpsat_wrapper.py)

**Notes**:
- TypedDict used for type safety without runtime overhead
- Frozen dataclass prevents bugs from mutation during backtracking
- Time format: minutes from midnight allows simple numeric comparisons
- Schedule status can be inferred from enrolled field but included for clarity

---

### Module: core/parsing.py

**Purpose**: Parse human-readable schedule strings into normalized, machine-usable time representations.

**Primary Functions**:

```python
def time_to_minutes(time_str: str) -> int:
    """
    Converts HH:MM format (24-hour) to minutes from midnight.

    Args:
        time_str: Time in "HH:MM" format (e.g., "14:30")

    Returns:
        Integer minutes from midnight (0-1440)

    Example:
        time_to_minutes("14:30") → 870
    """

def parse_time_to_minutes(time_str: str) -> Optional[int]:
    """
    Parses time string with AM/PM notation to minutes from midnight.

    Args:
        time_str: Time string like "10:00 AM" or "3:45 PM"

    Returns:
        Minutes from midnight, or None if parsing fails

    Handles:
    - Case insensitive (am/AM/Am all work)
    - 12-hour format (1:00 AM - 12:59 PM)
    - Noon/midnight edge cases (12:00 AM = 0 min, 12:00 PM = 720 min)

    Example:
        parse_time_to_minutes("2:30 PM") → 870
        parse_time_to_minutes("12:00 AM") → 0
    """

def parse_schedule_string(schedule_string: str) -> Optional[ParsedSchedule]:
    """
    Parse complete schedule string into structured format.

    Args:
        schedule_string: Schedule like "MW 10:00 AM - 11:30 AM"

    Returns:
        ParsedSchedule dict with days, startTime, endTime, or None if invalid

    Parsing Steps:
    1. Split on first space to separate days from times
    2. Parse day abbreviations (M, T, W, Th, F, S, Su)
    3. Extract start time and end time using regex
    4. Convert both times to minutes from midnight
    5. Validate startTime < endTime

    Supported Formats:
    - Days: M, T, W, Th (not T+h), F, S, Su
    - Times: 12-hour with AM/PM (e.g., "10:00 AM")
    - Examples: "MW 10:00 AM - 11:30 AM", "TTh 01:00 PM - 03:00 PM"

    Example:
        parse_schedule_string("MW 10:00 AM - 11:30 AM") →
        {
            'days': ['M', 'W'],
            'startTime': 600,      # 10*60 = 600
            'endTime': 690         # 11*60 + 30 = 690
        }
    """
```

**Called By**:
- core/conflict.py → is_viable(), has_conflict()
- core/models.py → Section initialization
- scheduler/scheduler_engine.py → generate_schedules()
- verification/cpsat_wrapper.py → solve_with_cpsat()
- data_gen/synthetic.py → validate_problem()

**Error Handling**:
- Returns `None` on invalid input (not raising exceptions)
- Checks: non-empty string, valid day patterns, time format compliance, startTime < endTime
- Graceful degradation: calling code must handle None return values

**Flow**:
```
Input: "MW 10:00 AM - 11:30 AM"
  → Split to days="MW", times=" 10:00 AM - 11:30 AM"
  → Parse days ["M", "W"]
  → Regex match times "10:00 AM" and "11:30 AM"
  → parse_time_to_minutes("10:00 AM") → 600
  → parse_time_to_minutes("11:30 AM") → 690
  → Validate 600 < 690 ✓
  → Return {days: ['M', 'W'], startTime: 600, endTime: 690}
```

**Notes**:
- Day parsing handles "Th" edge case (doesn't split "Th" into "T" and "h")
- Time parsing uses regex with case insensitive flag
- All times stored in 24-hour minute format for comparison simplicity
- No storage of timezone information (assumes all times in same timezone)

---

## Feature Domain 2: Conflict Detection and Constraint Checking

### Pattern Overview

```
Section + Section + Constraints
    ↓
Conflict Detection (has_conflict, is_viable)
    ↓
Boolean: Can these sections coexist?
    ↓
Used during backtracking to prune invalid branches
```

Conflict detection implements two checks:
1. **Time conflicts**: Do two sections overlap in time on shared days?
2. **Viability**: Does a section satisfy constraint boundaries?

---

### Module: core/conflict.py

**Purpose**: Determine whether sections conflict and whether they satisfy constraints.

**Primary Functions**:

```python
def is_full(section: Section) -> bool:
    """
    Check if section has reached capacity.

    Args:
        section: Section with 'enrolled' field like "30/30"

    Returns:
        True if current enrollment >= total capacity

    Implementation:
    - Regex match "current/total" format
    - Extract integers
    - Compare current >= total

    Edge Cases:
    - Returns False if enrolled format invalid (no regex match)
    - "30/30" → True
    - "29/30" → False
    - "30/31" → False
    """

def is_at_risk(section: Section) -> bool:
    """
    Check if section has low enrollment or at-risk status.

    Args:
        section: Section with 'enrolled' field

    Returns:
        True if section meets any at-risk criteria:
        - current == 0 (zero enrollment)
        - total >= 20 AND current < 6 (large course with low enrollment)
        - total >= 10 AND current < 2 (medium course with minimal enrollment)

    Purpose:
    - Identify courses likely to be cancelled due to low enrollment
    - Can be filtered by constraint allowAt_risk flag

    Example:
        Section(..., enrolled="0/30", ...) → True (zero enrollment)
        Section(..., enrolled="3/25", ...) → True (large course, low enrollment)
        Section(..., enrolled="1/15", ...) → True (medium course, very low)
        Section(..., enrolled="10/30", ...) → False (adequate enrollment)
    """

def is_viable(section: Section, constraints: Constraints) -> bool:
    """
    Check if section satisfies all constraint requirements.

    Args:
        section: Section to validate
        constraints: Constraint dict with time window and enrollment filters

    Returns:
        True if section passes all checks

    Checks Performed:
    1. Schedule must parse successfully
    2. startTime >= constraints['earliestStart']
    3. endTime <= constraints['latestEnd']
    4. If allowFull=False: section must not be full
    5. If allowAt_risk=False: section must not be at-risk

    Example:
        constraints = {
            'earliestStart': '08:00',
            'latestEnd': '18:00',
            'allowFull': False,
            'allowAt_risk': True,
            ...
        }

        Section(1, "MW 7:00 AM - 8:30 AM", "15/30", "OK")
        → is_viable(section, constraints) → False (starts before 08:00)
    """

def has_conflict(s1: Section, s2: Section) -> bool:
    """
    Check if two sections have a time conflict.

    Args:
        s1, s2: Two sections to compare

    Returns:
        True if sections overlap in time

    Algorithm:
    1. Parse both sections' schedules (use cached parsed_schedule if available)
    2. Find shared day abbreviations (e.g., both have 'M')
    3. If no shared days → no conflict (return False)
    4. If shared days → check time overlap on those days
    5. Time overlap: startTime_a < endTime_b AND endTime_a > startTime_b

    Edge Cases:
    - Adjacent times do NOT conflict: "10:00-11:30" and "11:30-1:00" → False
    - Same day, different times: "M 10:00-11:30" and "M 1:00-2:30" → False
    - Same time, different days: "M 10:00-11:30" and "W 10:00-11:30" → False
    - Full overlap: "MW 10:00-11:30" and "MW 10:00-11:30" → True

    Example:
        s1 = Section(1, "MW 10:00 AM - 11:30 AM", "15/30", "OK")
        s2 = Section(2, "MW 11:00 AM - 12:30 PM", "15/30", "OK")
        has_conflict(s1, s2) → True (both M, times overlap)

        s3 = Section(3, "TTh 10:00 AM - 11:30 AM", "15/30", "OK")
        has_conflict(s1, s3) → False (no shared days)
    """
```

**Called By**:
- scheduler/scheduler_engine.py → generate_schedules() (viability filtering + conflict checking)
- verification/cpsat_wrapper.py → solve_with_cpsat() (constraint encoding)
- test_scheduler.py → Unit tests

**Error Handling**:
- Returns `False` gracefully if parsing fails (conservative: assumes no conflict)
- Regex failures for enrolled format return `False` for is_full/is_at_risk
- Missing parsed_schedule triggers inline parsing (no errors, just slower)

**Performance Characteristics**:
- `is_viable()`: O(1) - single viability check per section
- `has_conflict()`: O(1) - fixed number of day comparisons
- Called O(n²) times during scheduling (n = number of sections) → O(n²) overall

**Notes**:
- Conflict detection is core to pruning effectiveness in backtracking
- Caching parsed_schedule in Section avoids re-parsing during algorithm execution
- At-risk heuristics are domain-specific (based on course enrollment research)
- Viability filtering happens once before backtracking starts

---

## Feature Domain 3: Scheduling Engine (Variation 1 - Backtracking)

### Pattern Overview

```
Input: Course Sections, Constraints
    ↓
Filter Viable Sections
    ↓
Backtracking Search:
  For each course (step):
    For each viable section:
      If no conflict with current schedule:
        Recurse to next course
      Else:
        Prune and try next section
    Backtrack if no valid sections
    ↓
Collect All Valid Schedules
    ↓
Output: List[GeneratedSchedule], Statistics
```

The scheduling engine implements **recursive backtracking with conflict-based pruning** to find all feasible course schedules within a given constraint set.

---

### Module: scheduler/scheduler_engine.py

**Purpose**: Generate all feasible course schedules using backtracking with conflict detection.

**Primary Functions**:

```python
def generate_schedules(
    course_sections: List[List[Section]],
    constraints: Constraints,
    enable_tracing: bool = False
) -> Tuple[List[GeneratedSchedule], Dict[str, Any]]:
    """
    Generate all feasible schedules by backtracking search.

    Args:
        course_sections: List of courses, where each course is List[Section]
                        Example: [
                          [Section(1, "MW 09:00...", ...), Section(2, "MW 14:00...", ...)],  # Course 0
                          [Section(1, "TTh 09:00...", ...)],  # Course 1
                        ]
        constraints: Constraints dict with time window and limits
        enable_tracing: If True, collect detailed trace logs

    Returns:
        Tuple of:
        - List[GeneratedSchedule]: All valid schedules found
        - Dict[str, Any]: Statistics dict with metrics

    Algorithm:
    1. Pre-filter: Remove sections that violate constraints (time window, full, at-risk)
    2. If any course has no viable sections → return empty (infeasible)
    3. Backtrack recursively:
       - Base case: all courses assigned → validate and store schedule
       - Recursive: for each viable section of current course
         * Check if it conflicts with already-selected sections
         * If no conflict → recurse to next course
         * If conflict → try next section
    4. Stop when maxSchedules reached
    5. Return all found schedules + statistics

    Complexity:
    - Time: O(n₁ × n₂ × ... × nₖ) where nᵢ = viable sections for course i
    - Worst case: O(m^c) where m = max sections/course, c = num courses
    - Typical case: much faster due to conflict pruning
    - Space: O(c) recursion depth + O(r) result storage (r = valid schedules)

    Example:
        courses = [
            [Section(1, "MW 09:00 AM - 10:30 AM", "15/30", "OK")],
            [Section(1, "MW 10:00 AM - 11:30 AM", "15/30", "OK"),
             Section(2, "TTh 09:00 AM - 10:30 AM", "15/30", "OK")]
        ]
        constraints = {
            'earliestStart': '08:00',
            'latestEnd': '18:00',
            'allowFull': True,
            'allowAt_risk': True,
            'maxSchedules': 10,
            'maxFullPerSchedule': 1
        }

        schedules, stats = generate_schedules(courses, constraints)
        # schedules[0] = {
        #     'selections': [Section(1, "MW 09:00...", ...), Section(2, "TTh 09:00...", ...)],
        #     'parsed': [ParsedSchedule(...), ParsedSchedule(...)],
        #     'meta': {'fullCount': 0, 'endsByPreferred': True, 'hasLate': False, 'latestEnd': 630}
        # }
        # stats = {
        #     'nodes_explored': 42,
        #     'valid_schedules': 1,
        #     'pruned_by_conflict': 5,
        #     'pruned_by_viability': 10,
        #     'pruned_by_full': 0,
        #     'execution_time_ms': 3.45
        # }
    """

def create_schedule_object(
    sections: List[Section],
    constraints: Constraints
) -> GeneratedSchedule:
    """
    Build a schedule object from selected sections.

    Args:
        sections: List of selected sections forming a schedule
        constraints: Constraints dict (used for preferred end time)

    Returns:
        GeneratedSchedule with selections, parsed schedules, and metadata

    Metadata Computation:
    - fullCount: Number of sections where current == total
    - endsByPreferred: latestEnd <= constraints['latestEnd'] in minutes?
    - hasLate: Any section starts >= 12:00 (noon)?
    - latestEnd: Maximum end time in minutes across all sections

    Purpose:
    - Package results for output
    - Provide metadata for result filtering/sorting
    - Enable quality-based schedule ranking
    """
```

**Called By**:
- interfaces/cli.py → run_cli() (CLI mode execution)
- interfaces/tui.py → run_algorithm() (TUI mode execution)
- test_scheduler.py → test_generate_schedules() (unit tests)

**Calls**:
- core/conflict.py → is_viable(), has_conflict()
- core/parsing.py → parse_schedule_string()
- core/models.py → Section, Constraints, GeneratedSchedule types
- scheduler/statistics.py → Statistics class
- scheduler/tracing.py → Tracing class

**Data Flow**:
```
generate_schedules([course0, course1, ...], constraints)
  ↓
Create Statistics() and Tracing() objects
  ↓
Pre-filter each course: viable_lists = [
    [Section(viable), Section(viable), ...],  # Course 0
    [Section(viable), ...],                   # Course 1
  ]
  ↓
Call backtrack(step=0, current_selection=[])
  ├─ For course 0: try each viable section
  │  └─ For each section:
  │     └─ Check conflicts with current_selection (empty)
  │        └─ Recurse: backtrack(1, [section])
  │
  ├─ For course 1: try each viable section
  │  └─ For section that doesn't conflict:
  │     └─ Recurse: backtrack(2, [sect0, sect1])
  │
  └─ Base case: step == len(viable_lists)
     └─ Create GeneratedSchedule from current_selection
     └─ Store in results if valid
  ↓
Return (results, stats.get_stats())
```

**Error Handling**:
- Returns empty list if any course has zero viable sections (infeasible)
- Conflict checking handles sections with unparseable schedules (returns False)
- Graceful degradation: missing parsed_schedule triggers inline parsing (slower but correct)

**Performance Optimizations**:
1. **Viability pre-filtering**: Eliminates sections violating time window before backtracking
2. **Parsed schedule caching**: Avoids re-parsing same schedule string multiple times
3. **Conflict short-circuit**: `any()` returns on first True (doesn't check all previously selected)
4. **Early stopping**: Stops when maxSchedules reached (doesn't explore full search space)

**Notes**:
- **No heuristic ordering**: Processes courses in input order (not Most-Constrained-First)
- **No forward checking**: Doesn't verify remaining courses still feasible after selection
- **Simple pruning**: Only removes conflicting branches, not infeasible subproblems
- **Multiple solutions**: Explores entire solution space up to maxSchedules limit

---

### Module: scheduler/statistics.py

**Purpose**: Collect metrics about backtracking execution for analysis.

**Primary Class**: `Statistics`

```python
class Statistics:
    """
    Accumulates counters during backtracking execution.

    Tracks:
    - nodes_explored: Total backtrack() calls (search tree size)
    - valid_schedules: Number of complete schedules generated
    - pruned_by_conflict: Sections rejected due to time conflicts
    - pruned_by_viability: Sections rejected before backtracking
    - pruned_by_full: Complete schedules rejected (too many full sections)
    """

    def __init__(self):
        """Initialize counters and start timer."""
        self.nodes_explored = 0
        self.valid_schedules = 0
        self.pruned_by_conflict = 0
        self.pruned_by_viability = 0
        self.pruned_by_full = 0
        self.start_time = time.time()

    def get_stats(self) -> Dict[str, Any]:
        """
        Return collected statistics as dictionary.

        Returns:
            {
                'nodes_explored': int,
                'valid_schedules': int,
                'pruned_by_conflict': int,
                'pruned_by_viability': int,
                'pruned_by_full': int,
                'execution_time_ms': float
            }
        """
```

**Called By**:
- scheduler/scheduler_engine.py → generate_schedules()

**Usage**:
```python
stats = Statistics()
# ... during backtracking ...
stats.increment_node()
stats.increment_pruned_conflict()
# ... get results ...
results = stats.get_stats()
print(f"Explored {results['nodes_explored']} nodes in {results['execution_time_ms']:.2f}ms")
```

---

### Module: scheduler/tracing.py

**Purpose**: Optionally log detailed decision traces for debugging and analysis.

**Primary Class**: `Tracing`

```python
class Tracing:
    """
    Records decision tree if enabled.

    Logs:
    - [TRY] - Attempting to use a section
    - [PRUNE] - Removing a branch with reason
    - [BACKTRACK] - Backtracking event
    - [VALID] - Schedule found and stored
    """

    def __init__(self, enabled: bool = False):
        """Initialize with enable flag."""
        self.enabled = enabled
        self.traces: List[str] = []

    def get_trace(self) -> str:
        """Return full trace as formatted multi-line string."""

    def get_trace_list(self) -> List[str]:
        """Return trace as list of individual entries."""
```

**Called By**:
- scheduler/scheduler_engine.py → generate_schedules()

**Purpose**: Enable debugging of backtracking decisions (which branches explored, why pruned, etc.)

---

## Feature Domain 4: Data Generation and Input Loading

### Pattern Overview

```
Input Source (CSV file or synthetic generation)
    ↓
Load/Generate Problem Data
    ↓
Validation
    ↓
Problem: Dict[course_name] = List[Section]
    ↓
Ready for scheduling algorithm
```

Data generation provides two paths: loading from CSV and generating synthetic problems.

---

### Module: data_gen/csv_loader.py

**Purpose**: Load course sections from CSV files into structured Section objects.

**Primary Functions**:

```python
def load_csv(
    filepath: str,
    group_col: str = "group",
    schedule_col: str = "schedule",
    enrolled_col: str = "enrolled",
    status_col: str = "status"
) -> List[List[Section]]:
    """
    Load CSV and return sections grouped by course.

    Args:
        filepath: Path to CSV file
        group_col: Column name for section group/number
        schedule_col: Column name for schedule string
        enrolled_col: Column name for enrollment (e.g., "25/30")
        status_col: Column name for status

    Returns:
        List[List[Section]] where each inner list is sections for one course

    Grouping Logic:
    - Extracts course ID as (group // 100)
    - Example: group 101, 102 → course_id 1
    - Example: group 201, 202, 203 → course_id 2
    - Returns sections sorted by course_id

    CSV Format Expected:
        group,schedule,enrolled,status
        101,MW 10:00 AM - 11:30 AM,25/30,OK
        102,MW 01:00 PM - 02:30 PM,30/30,FULL
        201,TTh 09:00 AM - 10:30 AM,15/30,OK

    Example:
        problem = load_csv("courses.csv")
        # Returns:
        # [
        #   [Section(101, ...), Section(102, ...)],  # Course 1
        #   [Section(201, ...)]                      # Course 2
        # ]
    """

def load_csv_flat(filepath: str, ...) -> List[Section]:
    """
    Load CSV and return flat list of all sections (no grouping).

    Useful when course grouping not needed.
    """

def load_csv_real_data(filepath: str) -> List[List[Section]]:
    """
    Load CSV in real dataset format with course metadata.

    Expected columns: Course Code, Course Name, Group, Schedule, Enrolled
    - Automatically infers status: "full" if current == total, else "open"
    - Groups by Course Code instead of numeric course_id

    Example:
        Course Code,Course Name,Group,Schedule,Enrolled
        CIS 3100,Data Structures,1,MW 10:00 AM - 11:30 AM,25/30
        CIS 3100,Data Structures,2,TTh 10:00 AM - 11:30 AM,20/30
    """

def auto_detect_format(filepath: str) -> str:
    """
    Detect CSV format by checking column headers.

    Returns:
    - "real" if has "Course Code" column
    - "simple" if using basic format

    Used to automatically choose appropriate loader.
    """
```

**Error Handling**:
- Raises `FileNotFoundError` if file doesn't exist
- Raises `ValueError` if required columns missing or data invalid
- Validates: group is integer, required fields not empty
- Provides helpful error messages with context

**Called By**:
- interfaces/cli.py → run_cli() (CLI data loading)
- interfaces/tui.py → load_data_csv() (TUI data loading)
- test_scheduler.py (unit tests)

---

### Module: data_gen/config_loader.py

**Purpose**: Load scheduling constraints from YAML/JSON configuration files.

**Primary Functions**:

```python
def load_config(filepath: str) -> Constraints:
    """
    Load constraint configuration from YAML or JSON file.

    Supports YAML format:
        constraints:
          earliestStart: "08:00"
          latestEnd: "18:00"
          allowFull: false
          allowAt_risk: true
          maxSchedules: 5
          maxFullPerSchedule: 1

    Validation:
    - All required fields must be present
    - Type validation: earliestStart/latestEnd are strings (HH:MM format)
    - Value validation: maxSchedules >= 0, valid time format
    - Helpful error messages on failure

    Returns:
        Constraints TypedDict with validated values

    Raises:
        FileNotFoundError: File doesn't exist
        ValueError: Missing/invalid constraints
    """

def load_config_with_defaults(filepath: Optional[str] = None) -> Constraints:
    """
    Load config from file, or return defaults if no file specified.

    Default Values:
    - earliestStart: "08:00"
    - latestEnd: "18:00"
    - allowFull: False
    - allowAt_risk: True
    - maxSchedules: 50
    - maxFullPerSchedule: 0

    Useful for optional constraint specification.
    """
```

**Called By**:
- interfaces/cli.py → run_cli() (optional config loading)
- Potentially by future TUI enhancements

---

### Module: data_gen/synthetic.py

**Purpose**: Generate random timetabling problem instances at varying sizes and constraint tightness for research.

**Primary Functions**:

```python
def generate_problem(
    size: str,
    tightness: str,
    seed: int = None
) -> Dict[str, List[Section]]:
    """
    Generate synthetic problem instance.

    Args:
        size: 'small' (5), 'medium' (20), or 'large' (50) courses
        tightness: 'loose' (3-5 sections/course) or 'tight' (2 sections/course)
        seed: Optional random seed for reproducibility

    Returns:
        Dict mapping course names to lists of Section objects
        {
            'COURSE_001': [Section(...), Section(...), ...],
            'COURSE_002': [Section(...)],
            ...
        }

    Generation Process:
    1. Generate N courses (based on size)
    2. For each course: randomly choose 2-5 sections (based on tightness)
    3. For each section:
       - Random day pattern: MW, TTh, MWF, T, or Th
       - Random start hour: 8 AM to 3 PM (8-15)
       - Duration: 1 hour
       - Random enrollment: 0-30 out of 30
       - Status: "full" if enrolled==30, else "open"

    Example:
        problem = generate_problem('small', 'loose', seed=42)
        # Generates 5 courses with 3-5 sections each
        # Same seed produces identical problem (reproducibility)
    """

def generate_problem_batch(
    configs: List[Tuple[str, str]],
    seed: int = None
) -> Dict[str, Dict[str, List[Section]]]:
    """
    Generate multiple problem instances with different configurations.

    Args:
        configs: List of (size, tightness) tuples
        seed: Base seed for reproducibility

    Returns:
        Nested dict: {'small_loose': {...}, 'medium_tight': {...}, ...}

    Example:
        batch = generate_problem_batch([
            ('small', 'loose'),
            ('medium', 'tight'),
            ('large', 'loose')
        ], seed=42)
    """

def get_problem_stats(problem: Dict[str, List[Section]]) -> Dict:
    """
    Calculate statistics about a problem instance.

    Returns:
        {
            'total_courses': int,
            'total_sections': int,
            'avg_sections_per_course': float,
            'time_range_coverage': List[int]  # Hours 0-23
        }
    """

def save_problem(problem: Dict[str, List[Section]], filepath: str) -> None:
    """
    Serialize problem instance to JSON file.

    Converts Section dataclasses to dicts, writes JSON.
    """

def load_problem(filepath: str) -> Dict[str, List[Section]]:
    """
    Deserialize problem instance from JSON file.

    Reconstructs Section objects from JSON.
    """

def validate_problem(
    problem: Dict[str, List[Section]]
) -> Tuple[bool, List[str]]:
    """
    Validate problem instance for correctness.

    Returns:
        (is_valid: bool, errors: List[str])

    Checks:
    - All courses have at least one section
    - All schedule strings parse correctly
    - All required Section fields present
    """
```

**Called By**:
- interfaces/cli.py → run_cli() (--generate flag)
- interfaces/tui.py → load_data_synthetic() (TUI synthetic mode)
- tests/ → benchmark tests

**Purpose**: Enable reproducible research by generating consistent test problems at various difficulty levels

---

## Feature Domain 5: CP-SAT Verification

### Pattern Overview

```
Problem: Dict[course] = List[Section]
    ↓
CP-SAT Model Construction:
  - Decision variables: section selection per course
  - Constraints: exactly one section per course, no time conflicts
    ↓
Solve with OR-Tools CP-SAT Solver
    ↓
Result: {feasible, solution, status, runtime_ms, optimal}
    ↓
Compare with backtracking results
```

CP-SAT verification provides an industrial-strength constraint solver for benchmarking backtracking against.

---

### Module: verification/cpsat_wrapper.py

**Purpose**: Solve timetabling problem using Google OR-Tools CP-SAT solver for verification.

**Primary Functions**:

```python
def solve_with_cpsat(
    problem: Dict[str, List[Section]],
    constraints: Optional[Constraints] = None,
    time_limit_s: float = 10.0
) -> Dict:
    """
    Solve timetabling problem using CP-SAT solver.

    Args:
        problem: Dict mapping course names to lists of Section objects
        constraints: Optional constraints (not used in basic solver,
                    included for API compatibility)
        time_limit_s: Maximum solver time in seconds (default 10)

    Returns:
        Result dictionary:
        {
            'feasible': bool,           # Solution found?
            'solution': dict,           # {course: Section} mapping
            'status': str,              # 'OPTIMAL', 'FEASIBLE', 'INFEASIBLE', 'UNKNOWN'
            'runtime_ms': float,        # Solver execution time
            'objective_value': float,   # 0 for feasibility-only
            'optimal': bool             # Proven optimal?
        }

    Algorithm:
    1. Create CP-SAT model
    2. Parse all section schedules
    3. Create binary decision variables:
       - x[course_i][section_j] = 1 if section_j selected for course_i
    4. Add constraints:
       - Constraint 1: Exactly one section per course
         sum(x[i][*]) == 1 for all courses i
       - Constraint 2: No time conflicts
         For each pair of sections (i,j) that conflict:
           x[course_i][section_i] + x[course_j][section_j] <= 1
    5. Solve with time limit
    6. Extract solution from solver

    Complexity:
    - Model size: O(c × s) variables where c = courses, s = max sections/course
    - Constraints: O(c) + O(c² × s²) for conflict constraints
    - Solver: Heuristic-based with 10s timeout (exact timing data-dependent)

    Example:
        problem = {
            'MATH_101': [Section(1, 'MW 10:00 AM - 11:30 AM', '15/30', 'OK')],
            'CS_101': [Section(1, 'TTh 10:00 AM - 11:30 AM', '20/30', 'OK')]
        }
        result = solve_with_cpsat(problem, time_limit_s=5)

        if result['feasible']:
            for course, section in result['solution'].items():
                print(f"{course}: {section.schedule}")
        else:
            print("Problem is infeasible")
    """

def _has_time_conflict(
    parsed_schedule_a: Dict,
    parsed_schedule_b: Dict
) -> bool:
    """
    Check if two parsed schedules conflict (internal helper).

    Used during model construction to identify conflicting section pairs.
    """
```

**Called By**:
- interfaces/cli.py → run_cli() (--verify flag)
- interfaces/tui.py → run_algorithm() (verify=True mode)
- tests/ → verification tests

**Data Flow**:
```
solve_with_cpsat(problem, time_limit_s=10)
  ↓
Create CpModel()
  ↓
Parse all section schedules into ParsedSchedule dicts
  ↓
Create decision variables:
  selection_vars[course_i] = [BoolVar(...), BoolVar(...), ...]
  ↓
Add constraint: sum(selection_vars[course_i]) == 1
  ↓
For each conflicting pair of sections (i, j):
  Add constraint: var_i + var_j <= 1
  ↓
Create CpSolver(), set max_time_in_seconds
  ↓
status = solver.Solve(model)
  ↓
Extract solution: for each course, find selected section
  ↓
Return result dict with feasibility, solution, status, runtime
```

**Error Handling**:
- Returns `feasible=False` if schedule parsing fails
- Gracefully handles timeout: returns best solution found so far (FEASIBLE vs OPTIMAL distinction)
- Handles infeasible problems: status='INFEASIBLE', feasible=False

**Performance Characteristics**:
- Model creation: O(c² × s²) for conflict constraint enumeration
- Solver: Varies by problem size, typically 10-1000ms for small-medium problems
- May timeout on large hard instances (50+ courses with many conflicts)

**Notes**:
- Used for benchmarking, not production scheduling
- Not applied in interfaces (only CLI/TUI verification mode)
- Time limit prevents unbounded solver execution
- Finds proven optimal solution if time permits

---

## Feature Domain 6: Interfaces (CLI and TUI)

### Pattern Overview

```
Entry Point: main.py --interactive or main.py --algo backtracking_v1 --input data.csv
    ↓
Route to: TUI (interactive) or CLI (scriptable)
    ↓
Load Data → Setup Constraints → Run Algorithm → [Verify] → Format Output
```

Two execution modes: CLI for batch processing and TUI for interactive exploration.

---

### Module: main.py

**Purpose**: Entry point for both CLI and TUI execution modes.

**Primary Functions**:

```python
def main():
    """
    Parse command-line arguments and route to appropriate mode.

    Arguments:
    - --interactive: Enter interactive TUI mode
    - --algo: Algorithm name (e.g., "backtracking_v1")
    - --input: Input CSV file path
    - --generate: Generate synthetic problem (e.g., "small_loose")
    - --verify: Run CP-SAT verification after backtracking
    - --verify-timeout: CP-SAT timeout in seconds (default 10)
    - --format: Output format "json" or "text"
    - --output: Output file path (default: stdout)
    - --max-schedules: Maximum schedules to find

    Examples:
        python3 main.py --interactive
        python3 main.py --algo backtracking_v1 --input courses.csv --format json
        python3 main.py --algo backtracking_v1 --generate small_loose --verify
    """
```

**Called By**: Python runtime via `python3 main.py [args]`

---

### Module: interfaces/cli.py

**Purpose**: Command-line interface for scriptable batch execution.

**Primary Functions**:

```python
def run_cli(args) -> int:
    """
    Execute CLI mode with parsed arguments.

    Execution Flow:
    1. Validate algorithm name (currently only backtracking_v1)
    2. Load data:
       - If --generate: create synthetic problem
       - If --input: load CSV file
    3. Setup constraints (hardcoded defaults, could be config-loaded)
    4. Run backtracking algorithm
    5. If --verify: run CP-SAT verification in parallel
    6. Format results (JSON or text)
    7. Output to file or stdout
    8. Return exit code (0 success, 1 error)

    Returns:
        0 on success, 1 on failure
    """
```

**Called By**:
- main.py → cli_mode()

**Output Formats**:
- JSON: Structured output with complete metadata
- Text: Human-readable dictionary string

**Example Usage**:
```bash
# Generate and verify
python3 main.py --algo backtracking_v1 --generate small_loose --verify

# Load from CSV and output to file
python3 main.py --algo backtracking_v1 --input courses.csv --format json --output results.json

# Batch processing with specific constraints
python3 main.py --algo backtracking_v1 --input courses.csv --max-schedules 10 --format json
```

---

### Module: interfaces/tui.py

**Purpose**: Interactive terminal UI with menu-driven exploration.

**Primary Functions**:

```python
def run_interactive():
    """
    Launch interactive TUI with menu-driven workflow.

    Flow:
    1. Display header and welcome
    2. Select algorithm (currently only Backtracking V1)
    3. Select data source (CSV or synthetic)
    4. Load/generate data
    5. Select run mode (standard or with verification)
    6. Configure constraints (or use defaults)
    7. Execute algorithm
    8. Display results with Rich formatting
    9. Option to try again or exit

    Uses Rich library for colored output and formatted tables.
    """

def select_algorithm() -> str:
    """Prompt user to choose algorithm"""

def select_data_source() -> str:
    """Prompt user for data source (CSV or synthetic)"""

def load_data_csv() -> Optional[Problem]:
    """Load data from CSV file"""

def load_data_synthetic() -> Optional[Problem]:
    """Generate synthetic problem with user parameters"""

def select_run_mode() -> bool:
    """Choose: standard or with verification"""

def run_algorithm(algo_name, problem, verify=False):
    """Execute algorithm and optionally verify"""
```

**Used By**: main.py → tui_mode()

**Example Workflow**:
```
1. Enter interactive mode
2. Choose "Backtracking V1"
3. Choose "Generate synthetic"
4. Enter: size=small, tightness=loose
5. Choose: "With Verification"
6. Algorithm runs and displays:
   - Backtracking results: 5 schedules in 12ms
   - CP-SAT results: 1 optimal in 45ms
   - Comparison table
   - Option to try another dataset
```

---

### Module: interfaces/output.py

**Purpose**: Format algorithm results for display.

**Primary Functions**:

```python
def format_verification_comparison(
    backtracking_result: Dict,
    cpsat_result: Dict
) -> Union[Table, str]:
    """
    Format side-by-side comparison of backtracking vs CP-SAT.

    Returns Rich Table if available, ASCII table otherwise.

    Displays:
    - Runtime comparison
    - Feasibility match/mismatch (color-coded)
    - Solution counts
    - Status and optimality
    """

def format_results_summary(
    solutions: list,
    elapsed_ms: float,
    problem_size: int
) -> str:
    """
    Format basic algorithm results summary.
    """

def format_solution_table(
    solutions: list,
    max_display: int = 5
) -> str:
    """
    Format individual solution details.

    Displays per-solution:
    - Schedule number
    - Number of courses
    - Full sections count
    - Ends by preferred time?
    """
```

**Called By**:
- interfaces/cli.py → run_cli()
- interfaces/tui.py → run_algorithm()

---

## Feature Domain 7: Testing Architecture

### Pattern Overview

```
Test Case (unittest framework)
    ↓
Setup: Create test data (Section objects, Constraints)
    ↓
Execute: Call parsing, conflict, or scheduling functions
    ↓
Assert: Verify expected results
    ↓
Teardown: Cleanup (implicit in unittest)
```

Tests verify correctness of core parsing, conflict detection, and scheduling logic.

---

### Module: test_scheduler.py

**Purpose**: Unit tests for core scheduling functionality.

**Test Structure**:

```python
class TestFunctionalEngine(unittest.TestCase):
    """Test parsing, conflict detection, scheduling core"""

    def test_parse_valid_mw(self):
        """Parse schedule string into correct ParsedSchedule"""
        result = parse_schedule_string("MW 10:00 AM - 11:30 AM")
        assert result['days'] == ['M', 'W']
        assert result['startTime'] == 600  # 10 * 60
        assert result['endTime'] == 690    # 11 * 60 + 30

    def test_has_conflict_overlapping(self):
        """Detect time conflicts on shared days"""
        s1 = Section(1, "MW 10:00 AM - 11:30 AM", "15/30", "OK")
        s2 = Section(2, "MW 11:00 AM - 12:30 PM", "15/30", "OK")
        assert has_conflict(s1, s2) == True

    def test_generate_schedules(self):
        """Generate valid non-conflicting schedules"""
        math = [Section(1, "MW 09:00 AM - 10:30 AM", "15/30", "OK")]
        cs = [Section(3, "TTh 09:00 AM - 10:30 AM", "15/30", "OK")]

        constraints = {
            'earliestStart': '08:00',
            'latestEnd': '18:00',
            'allowFull': True,
            'allowAt_risk': True,
            'maxSchedules': 10,
            'maxFullPerSchedule': 1
        }

        schedules, stats = generate_schedules([math, cs], constraints)
        assert len(schedules) == 1
        assert stats['nodes_explored'] > 0
```

**Test Categories**:

1. **Parsing Tests**:
   - Valid schedule formats (MW, TTh, MWF, etc.)
   - Time format parsing (12-hour with AM/PM)
   - Invalid format handling (None return)

2. **Conflict Tests**:
   - Overlapping times on shared days
   - Non-overlapping times on same day
   - Different days (no conflict)
   - Edge cases (adjacent times)

3. **Feasibility Tests**:
   - Time window constraints (earliestStart, latestEnd)
   - Full section filtering
   - At-risk enrollment filtering

4. **Scheduling Tests**:
   - Basic schedule generation
   - Conflict pruning effectiveness
   - Multiple solution discovery

**Execution**:
```bash
python3 -m pytest test_scheduler.py -v
python3 test_scheduler.py  # Direct execution
```

**Coverage**: Core parsing, conflict detection, and generation logic (approximately 70% of codebase)

---

### Module: tests/test_cpsat_integration.py

**Purpose**: Integration tests for CP-SAT verification.

**Structure**: Test cases for:
- Basic feasibility verification
- Solution validation
- Infeasible problem detection
- Timeout handling

---

## Cross-Feature Dependencies

### Dependency Graph

```
main.py (entry point)
├── interfaces/cli.py (CLI mode)
│   ├── data_gen/ (CSV/synthetic loading)
│   │   ├── csv_loader.py
│   │   └── synthetic.py
│   ├── scheduler/scheduler_engine.py (backtracking)
│   │   ├── core/models.py (types)
│   │   ├── core/parsing.py
│   │   ├── core/conflict.py (has_conflict, is_viable)
│   │   ├── scheduler/statistics.py
│   │   └── scheduler/tracing.py
│   ├── verification/cpsat_wrapper.py (CP-SAT verification)
│   │   ├── core/models.py
│   │   ├── core/parsing.py (parse_schedule_string)
│   │   └── OR-Tools cp_model
│   └── interfaces/output.py (result formatting)
│
└── interfaces/tui.py (TUI mode)
    ├── [same as CLI]
    └── Rich library (colored output)

test_scheduler.py
├── core/ (parsing, conflict, models)
├── scheduler/scheduler_engine.py
└── unittest framework

data_gen/ (independent module)
├── core/models.py (Section type)
└── core/parsing.py (parse_schedule_string)
```

### Module Isolation

**Independent Modules** (no internal dependencies):
- core/models.py - only Python builtins
- core/parsing.py - only Python builtins + regex
- core/conflict.py - only core/models, core/parsing

**Domain-Specific Modules** (depend on core):
- scheduler/scheduler_engine.py - depends on core + statistics + tracing
- verification/cpsat_wrapper.py - depends on core + OR-Tools
- data_gen/* - depends on core/models, core/parsing

**Interface Modules** (depend on many):
- interfaces/cli.py - depends on all above
- interfaces/tui.py - depends on all above + Rich
- main.py - depends on interfaces

**Test Modules** (depend on core + domain):
- test_scheduler.py - depends on core + scheduler_engine
- tests/test_cpsat_integration.py - depends on verification + core

---

## Grep-Friendly Index

### Data Structures

| Name | Location | Purpose |
|------|----------|---------|
| `ParsedSchedule` | core/models.py:5 | Type for parsed schedule (days, startTime, endTime) |
| `Section` | core/models.py:14 | Immutable dataclass for course section |
| `Constraints` | core/models.py:22 | TypedDict for scheduling constraints |
| `ScheduleMeta` | core/models.py:30 | Metadata about generated schedule (quality metrics) |
| `GeneratedSchedule` | core/models.py:36 | Schedule output format (selections + parsed + meta) |
| `Statistics` | scheduler/statistics.py:5 | Metrics accumulator (nodes_explored, valid_schedules, etc.) |
| `Tracing` | scheduler/tracing.py:4 | Optional decision trace logger |

### Parsing Functions

| Function | Location | Purpose |
|----------|----------|---------|
| `time_to_minutes(time_str)` | core/parsing.py:6 | HH:MM → minutes from midnight |
| `parse_time_to_minutes(time_str)` | core/parsing.py:12 | "10:00 AM" → minutes from midnight |
| `parse_schedule_string(schedule_string)` | core/parsing.py:30 | "MW 10:00 AM - 11:30 AM" → ParsedSchedule |

### Conflict and Viability Functions

| Function | Location | Purpose |
|----------|----------|---------|
| `is_full(section)` | core/conflict.py:6 | Is section at capacity? |
| `is_at_risk(section)` | core/conflict.py:14 | Low enrollment risk? |
| `is_viable(section, constraints)` | core/conflict.py:22 | Satisfies constraints? |
| `has_conflict(s1, s2)` | core/conflict.py:42 | Time overlap? |

### Scheduling Functions

| Function | Location | Purpose |
|----------|----------|---------|
| `generate_schedules(courses, constraints, enable_tracing)` | scheduler/scheduler_engine.py:179 | Main backtracking scheduler |
| `create_schedule_object(sections, constraints)` | scheduler/scheduler_engine.py:157 | Build GeneratedSchedule with metadata |

### Data Loading Functions

| Function | Location | Purpose |
|----------|----------|---------|
| `load_csv(filepath, group_col, schedule_col, enrolled_col, status_col)` | data_gen/csv_loader.py:13 | Load CSV → List[List[Section]] |
| `load_csv_flat(filepath, ...)` | data_gen/csv_loader.py:104 | Load CSV → List[Section] (flat) |
| `load_csv_real_data(filepath)` | data_gen/csv_loader.py:169 | Load real dataset format CSV |
| `auto_detect_format(filepath)` | data_gen/csv_loader.py:133 | Detect CSV format by headers |
| `load_config(filepath)` | data_gen/config_loader.py:19 | Load YAML/JSON constraints |
| `load_config_with_defaults(filepath)` | data_gen/config_loader.py:152 | Load config or use defaults |
| `generate_problem(size, tightness, seed)` | data_gen/synthetic.py:25 | Generate random problem |
| `generate_problem_batch(configs, seed)` | data_gen/synthetic.py:112 | Generate multiple problems |
| `get_problem_stats(problem)` | data_gen/synthetic.py:149 | Calculate problem metrics |
| `save_problem(problem, filepath)` | data_gen/synthetic.py:190 | Serialize problem to JSON |
| `load_problem(filepath)` | data_gen/synthetic.py:224 | Deserialize problem from JSON |
| `validate_problem(problem)` | data_gen/synthetic.py:258 | Verify problem correctness |

### Verification Functions

| Function | Location | Purpose |
|----------|----------|---------|
| `solve_with_cpsat(problem, constraints, time_limit_s)` | verification/cpsat_wrapper.py:19 | Solve with CP-SAT solver |
| `_has_time_conflict(parsed_a, parsed_b)` | verification/cpsat_wrapper.py:148 | Internal: check parsed schedule overlap |
| `_status_to_string(status)` | verification/cpsat_wrapper.py:177 | Internal: OR-Tools status → string |

### Interface Functions

| Function | Location | Purpose |
|----------|----------|---------|
| `main()` | main.py:27 | CLI argument parsing and routing |
| `cli_mode(args)` | main.py:17 | Route to CLI execution |
| `tui_mode()` | main.py:22 | Route to TUI execution |
| `run_cli(args)` | interfaces/cli.py:18 | Execute CLI workflow |
| `run_interactive()` | interfaces/tui.py | Execute TUI workflow |
| `format_verification_comparison(bt_result, cpsat_result)` | interfaces/output.py:72 | Format side-by-side comparison |
| `format_results_summary(solutions, elapsed_ms, problem_size)` | interfaces/output.py:131 | Format results summary |
| `format_solution_table(solutions, max_display)` | interfaces/output.py:162 | Format individual solution details |

### Classes and Methods

| Class | Method | Location | Purpose |
|-------|--------|----------|---------|
| `Statistics` | `increment_node()` | scheduler/statistics.py:16 | Increment backtrack node count |
| `Statistics` | `increment_valid_schedules()` | scheduler/statistics.py:20 | Increment found schedule count |
| `Statistics` | `increment_pruned_conflict()` | scheduler/statistics.py:24 | Increment conflict pruning count |
| `Statistics` | `increment_pruned_viability()` | scheduler/statistics.py:28 | Increment viability pruning count |
| `Statistics` | `increment_pruned_full()` | scheduler/statistics.py:32 | Increment full-section pruning count |
| `Statistics` | `get_stats()` | scheduler/statistics.py:36 | Return all accumulated statistics |
| `Tracing` | `log_try(course_idx, section)` | scheduler/tracing.py:11 | Log section attempt |
| `Tracing` | `log_prune(reason, detail)` | scheduler/tracing.py:16 | Log branch pruning |
| `Tracing` | `log_backtrack(step)` | scheduler/tracing.py:21 | Log backtrack event |
| `Tracing` | `log_valid_schedule(schedule_idx)` | scheduler/tracing.py:26 | Log schedule discovery |
| `Tracing` | `get_trace()` | scheduler/tracing.py:31 | Return trace as string |
| `Tracing` | `get_trace_list()` | scheduler/tracing.py:35 | Return trace as list |

---

## Performance Characteristics

### Parsing

| Function | Time | Space | Notes |
|----------|------|-------|-------|
| `time_to_minutes()` | O(1) | O(1) | Simple integer arithmetic |
| `parse_time_to_minutes()` | O(1) | O(1) | Regex match + parsing |
| `parse_schedule_string()` | O(1) | O(1) | Constant-size input (< 50 chars) |

### Conflict Detection

| Function | Time | Space | Notes |
|----------|------|-------|-------|
| `is_full()` | O(1) | O(1) | Single regex + comparison |
| `is_at_risk()` | O(1) | O(1) | Single regex + comparisons |
| `is_viable()` | O(1) | O(1) | Parsing + comparisons |
| `has_conflict()` | O(1) | O(1) | Fixed-size day comparisons |

### Scheduling Engine

| Aspect | Complexity | Typical Range | Notes |
|--------|-----------|----------------|-------|
| Time (backtracking) | O(n₁ × n₂ × ... × nₖ) worst case | 1-100ms for small-medium | Depends heavily on constraint tightness |
| Time (CP-SAT) | NP-hard, heuristic | 10-1000ms for small-medium | Time limit: 10s default |
| Space (backtracking) | O(k + r) | Negligible | k = course count, r = result count |
| Space (CP-SAT model) | O(c × s + c²) | ~1MB for typical problems | c = courses, s = sections/course |

### Typical Problem Sizes

| Problem Size | Courses | Sections | BT Time | CP-SAT Time | Feasible |
|--------------|---------|----------|---------|------------|----------|
| small_loose | 5 | 15-25 | 1-5ms | 10-50ms | 95% |
| small_tight | 5 | 10 | 2-8ms | 5-20ms | 70% |
| medium_loose | 20 | 60-100 | 10-50ms | 100-500ms | 80% |
| medium_tight | 20 | 40 | 50-200ms | 200-800ms | 40% |
| large_loose | 50 | 150-250 | 100-1000ms | 1-10s | 60% |
| large_tight | 50 | 100 | 500-5000ms | 5-60s | 20% |

---

## Implementation Patterns and Conventions

### Error Handling Philosophy

**Parse-or-None**: Parsing functions return `None` on invalid input rather than raising exceptions
```python
parsed = parse_schedule_string(user_input)
if parsed is None:
    # handle invalid input
```

**Early Exit**: Backtracking returns early if any course has zero viable sections
```python
if not viable:
    return [], stats.get_stats()  # Infeasible
```

**Type Safety**: TypedDict and frozen dataclass for compile-time type checking
```python
@dataclass(frozen=True)
class Section:
    ...  # Immutable, prevents accidental mutations
```

### Caching Strategy

**Lazy Parsing**: `Section.parsed_schedule` caches parsed schedule on first use
```python
parsed = section.parsed_schedule or parse_schedule_string(section.schedule)
```

**Pre-filtering**: Viability filtering happens once before backtracking
```python
viable_lists = []
for sections in course_sections:
    viable = [s for s in sections if is_viable(s, constraints)]
    viable_lists.append(viable)
```

### Testing Patterns

**Minimal Setup**: Tests create Section objects inline without fixtures
```python
s1 = Section(1, "MW 10:00 AM - 11:30 AM", "15/30", "OK")
```

**Immutability Verification**: Tests verify frozen dataclass prevents mutation
```python
section = Section(1, "MW 10:00 AM - 11:30 AM", "15/30", "OK")
# section.status = "FULL"  # Would raise FrozenInstanceError
```

---

## Known Limitations and Extension Points

### Current Limitations

1. **No Heuristic Ordering**: Processes courses in input order (not Most-Constrained-First)
   - Would improve: faster solution finding, better pruning
   - Could add: MCF ordering as scheduler option

2. **No Forward Checking**: Doesn't verify remaining courses still feasible after selection
   - Would improve: earlier detection of infeasible subproblems
   - Could add: forward_checking flag to generate_schedules()

3. **No Quality Optimization**: Finds feasible schedules but doesn't optimize quality
   - Would improve: can't rank schedules by preferred end time, minimal full sections, etc.
   - Could add: optimization objective to CP-SAT

4. **Single Algorithm Implementation**: Only backtracking_v1 available
   - Missing: Variation 2-4 implementations for professor/resource constraints
   - Could add: modular algorithm loader with swappable implementations

5. **No Constraint Configuration File Support in CLI**
   - Currently hardcoded constraints in interfaces/cli.py
   - Could add: --config flag to load from YAML/JSON

### Future Extension Points

1. **Heuristics Library**: Reusable Most-Constrained-First, Forward Checking, etc.
   ```python
   scheduler = SchedulerWithHeuristics(
       problem,
       constraints,
       heuristics=['mcf', 'forward_checking']
   )
   ```

2. **Algorithm Registry**: Dynamic algorithm loading
   ```python
   algo = AlgorithmLoader.load('backtracking_v1')
   # Could also load 'backtracking_v2_professor', etc.
   ```

3. **Constraint File Support**:
   ```bash
   python3 main.py --algo backtracking_v1 --input courses.csv --config constraints.yaml
   ```

4. **Parallel Backtracking**: Explore multiple branches simultaneously
   ```python
   scheduler.parallel = True
   scheduler.num_workers = 4
   ```

5. **Incremental Solution Report**: Stream solutions to output as found
   ```python
   for schedule in scheduler.generate_incremental():
       print(f"Found: {schedule}")
   ```

---

## Summary

This timetabling framework implements **Variation 1: Schedule Generation** with backtracking as the core algorithm. The architecture cleanly separates:

- **Core domain** (models, parsing, conflict detection)
- **Scheduling logic** (backtracking with viability filtering)
- **Data loading** (CSV, synthetic generation)
- **Verification** (CP-SAT benchmarking)
- **Interfaces** (CLI and TUI)
- **Testing** (unit tests)

The implementation prioritizes **correctness, clarity, and extensibility** for research purposes. No heuristics are yet implemented (baseline backtracking only), leaving room for incremental improvements and variation implementations.

