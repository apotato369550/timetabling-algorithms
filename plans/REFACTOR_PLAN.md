# Refactor Plan: Restructure for Extensibility

**Objective**: Reorganize codebase from monolithic script layout into extensible research framework. Structure first, then interface, then documentation.

**Rationale**: Current layout (algorithms mixed with CLI, utilities scattered) won't scale when adding Variations 2-4, new interfaces, or verification tools. Restructuring prevents future architectural debt.

---

## Phase 1: Reorganize Codebase (Foundation)

**Goal**: Create clean separation of concerns. Structure becomes source of truth for ARCHITECTURE.md.

### New Directory Layout

```
timetabling-algorithms/
├── algorithms/                    # Algorithm implementations (extensible)
│   ├── __init__.py
│   ├── base.py                   # AlgorithmBase (abstract class)
│   ├── loader.py                 # Dynamic algorithm discovery
│   └── variation_1/
│       ├── __init__.py
│       ├── backtracking.py       # Backtracking implementation
│       └── cpsat.py              # CP-SAT verification for V1
│
├── core/                          # Shared utilities (no algo-specific logic)
│   ├── __init__.py
│   ├── models.py                 # Section, ParsedSchedule, Constraints (TypedDicts + dataclasses)
│   ├── parsing.py                # parse_schedule_string(), time_to_minutes()
│   ├── conflict.py               # has_conflict(), is_viable() predicates
│   ├── tracing.py                # Trace infrastructure (existing tracing.py)
│   └── statistics.py             # Statistics collection (existing statistics.py)
│
├── interfaces/                    # Delivery modes (CLI/TUI/future)
│   ├── __init__.py
│   ├── cli.py                    # Scriptable interface (--input, --output json)
│   ├── tui.py                    # Terminal UI (interactive mode)
│   └── output.py                 # Shared formatting (tables, JSON, trace trees)
│
├── data_gen/                      # Data generation & loading
│   ├── __init__.py
│   ├── csv_loader.py             # Load courses from CSV (existing)
│   ├── config_loader.py          # Load constraints from YAML (existing)
│   └── synthetic.py              # Generate synthetic problems (small/medium/large)
│
├── verification/                  # CP-SAT verification (isolated concern)
│   ├── __init__.py
│   └── cpsat_wrapper.py          # Generic CP-SAT runner for comparison
│
├── main.py                        # Entry point (replaces scheduler_cli.py)
├── test_scheduler.py             # Tests (existing, will refactor to use new structure)
├── README.md                      # User manual (documentation)
├── CLAUDE.md                      # Project philosophy (documentation)
├── ARCHITECTURE.md               # Implementation reference (documentation)
├── CHANGELOG.md                  # Version history (documentation)
├── plans/                         # Planning docs (this dir)
├── data/                          # Test datasets (existing)
└── docs/                          # Supporting docs (existing)
```

### What Each Module Owns

| Module | Responsibility | Import From |
|--------|---|---|
| `core/models.py` | Data structures (Section, Constraints, ParsedSchedule) | Nothing core-internal |
| `core/parsing.py` | Schedule string parsing | models.py |
| `core/conflict.py` | Conflict detection, viability checking | parsing.py, models.py |
| `core/tracing.py` | Trace logging infrastructure | models.py |
| `core/statistics.py` | Metrics collection | (no dependencies) |
| `algorithms/base.py` | AlgorithmBase class | core/* |
| `algorithms/variation_1/backtracking.py` | Backtracking implementation | core/*, base.py |
| `algorithms/variation_1/cpsat.py` | CP-SAT verification | core/*, base.py, ortools |
| `algorithms/loader.py` | Dynamic algorithm discovery | base.py |
| `data_gen/csv_loader.py` | Load CSV → Section objects | core/models.py |
| `data_gen/synthetic.py` | Generate random problems | core/models.py |
| `verification/cpsat_wrapper.py` | Generic CP-SAT runner | core/*, ortools |
| `interfaces/output.py` | Format results (tables, JSON) | core/models.py |
| `interfaces/cli.py` | CLI interface | algorithms/loader.py, interfaces/output.py, data_gen/*, verification/* |
| `interfaces/tui.py` | Terminal UI | algorithms/loader.py, interfaces/output.py, data_gen/*, verification/* |
| `main.py` | Entry point | interfaces/cli.py, interfaces/tui.py |

### Why This Structure Scales

- **New algorithm**: Create `algorithms/variation_2/` with new implementation. Loader picks it up automatically.
- **New interface**: Add file to `interfaces/`. Both CLI and TUI share core + output formatting.
- **New verification**: Extend `verification/`. Interfaces consume it without coupling.
- **Core changes**: Affect all algos uniformly (only place shared logic lives).

---

## Phase 2: Refactor Existing Code Into New Structure

**Goal**: Move existing code into new directories, extract shared utilities.

### Work Breakdown

**2.1 Extract Core Utilities**
- `core/models.py`: Move Section, ParsedSchedule, Constraints from scheduler_engine.py
- `core/parsing.py`: Move parse_schedule_string(), parse_time_to_minutes(), time_to_minutes()
- `core/conflict.py`: Move has_conflict(), is_viable(), is_full(), is_at_risk()
- `core/tracing.py`: Move existing tracing.py (minimal changes)
- `core/statistics.py`: Move existing statistics.py (minimal changes)

**2.2 Refactor Algorithms**
- `algorithms/base.py`: Create AlgorithmBase abstract class
  ```python
  class AlgorithmBase:
      def solve(self, problem: Problem, constraints: Constraints) -> List[Solution]:
          """Return list of valid solutions"""
          raise NotImplementedError

      def get_trace(self) -> TraceData:
          """Return execution trace for visualization"""
          raise NotImplementedError

      @staticmethod
      def metadata() -> Dict[str, Any]:
          """Algorithm name, description, version"""
          raise NotImplementedError
  ```
- `algorithms/variation_1/backtracking.py`: Refactor scheduler_engine.generate_schedules() → BacktrackingAlgorithm class inheriting AlgorithmBase
- `algorithms/loader.py`: Implement dynamic loading (scan algorithms/ dirs, instantiate classes)

**2.3 Move Data Loading**
- `data_gen/csv_loader.py`: Move existing csv_loader.py (minimal changes)
- `data_gen/config_loader.py`: Move existing config_loader.py (minimal changes)
- `data_gen/synthetic.py`: NEW - Generate random problem instances (small/medium/large)

**2.4 Preserve Verification**
- `verification/cpsat_wrapper.py`: NEW - Generic CP-SAT runner that takes a problem, returns solution + metadata

### Parallelization

**Agent A**: Extract core utilities (models, parsing, conflict detection)
**Agent B**: Refactor algorithms (create base class, move backtracking, build loader)
**Agent C**: Move/enhance data loading (csv_loader, config_loader, synthetic generator)
**Agent D**: Implement verification wrapper (CP-SAT integration)

These run in parallel. Minimal dependencies until Phase 3.

---

## Phase 3: Implement Algorithm Loader + Dual Interface

**Goal**: Build interface layer (CLI + TUI) that both consume algorithm engine.

### 3.1 Algorithm Loader (`algorithms/loader.py`)

```python
def load_algorithms() -> Dict[str, AlgorithmBase]:
    """Scan algorithms/ directory, instantiate all AlgorithmBase subclasses"""
    # Returns {name: instance} dict
    # E.g., {'backtracking_v1': BacktrackingAlgorithm(), ...}

def get_algorithm(name: str) -> AlgorithmBase:
    """Get algorithm by name, raise if not found"""
```

### 3.2 Interfaces (`interfaces/`)

**CLI Mode** (`cli.py`):
```bash
python3 main.py --algo backtracking_v1 \
                --input data.csv \
                --config config.yaml \
                --trace \
                --format json \
                --output results.json
```

- Scriptable (pipes to agents)
- JSON output (machine-readable)
- Returns exit code for automation

**TUI Mode** (`tui.py`):
```bash
python3 main.py --interactive
# Interactive menu: choose algo → load data → run → view results (tables)
```

- Human-friendly
- ASCII tables for schedules
- Trace trees displayed
- Metrics summary

**Shared Output** (`output.py`):
- Format schedule as table (rich.Table)
- Format trace as tree (ASCII or JSON)
- Format results as JSON
- Format statistics summary

### 3.3 Entry Point (`main.py`)

Detects mode (CLI vs. TUI) from arguments, delegates to appropriate interface.

---

## Phase 4: Data Generation + Verification Integration

**Goal**: Build data generation and CP-SAT verification as first-class features.

### 4.1 Synthetic Problem Generator (`data_gen/synthetic.py`)

```python
def generate_problem(size: str, tightness: str) -> Problem:
    """
    size: 'small' (5 courses), 'medium' (20), 'large' (50+)
    tightness: 'loose' (many solutions), 'tight' (few solutions)
    Returns: Problem with random courses/sections
    """
```

- Used for benchmarking
- Controlled problem parameters
- Reproducible (seed support)

### 4.2 CP-SAT Verification (`verification/cpsat_wrapper.py`)

```python
def solve_with_cpsat(problem: Problem, constraints: Constraints, time_limit_s: int = 10) -> Solution:
    """
    Encodes problem in CP-SAT, solves, returns solution.
    Used for comparing backtracking solutions to optimal.
    """
```

### 4.3 Integration

Both interfaces (CLI/TUI) can:
- Generate synthetic problems (`--generate small`)
- Solve with algorithm (`--algo backtracking_v1`)
- Verify with CP-SAT (`--verify`)
- Compare results (runtime, quality, optimality gap)

---

## Phase 5: Document What Actually Exists

**Goal**: Write documentation grounded in real structure (not the reverse).

### 5.1 ARCHITECTURE.md

- Feature domains: Core (models, parsing, conflict), Algorithms (loader, base, V1), Interfaces (CLI, TUI), Data (generation, loading)
- For each function: Purpose, Input/Output, Called By/Calls, Errors
- Grep-Friendly Index with line numbers
- No speculation; only what exists

### 5.2 CLAUDE.md

- Vision: Research framework for timetabling algorithm exploration
- Philosophy: Why backtracking matters, when to use which paradigm
- Design Decisions: Why split core/algorithms/interfaces, why AlgorithmBase pattern
- Common Gotchas: Schedule parsing edge cases, conflict detection, backtracking explosion
- Success Metrics: New algos load without modifying core, verification compares correctly

### 5.3 README.md

- Quick start: Install → Run → View results
- CLI examples (scriptable usage)
- TUI walkthrough (human usage)
- How to add new algorithm (inherit AlgorithmBase, implement solve/get_trace)
- Troubleshooting

---

## Implementation Sequencing

**Phase 1 (Foundation)**: Create new directory structure (no code changes yet)
- Status: Directory tree exists, empty __init__.py files

**Phase 2 (Refactoring)**: Move/extract code
- Agent A: Core utilities
- Agent B: Algorithms (base class + backtracking)
- Agent C: Data generation
- Agent D: Verification
- **Run in parallel**
- Tests updated to use new imports

**Phase 3 (Interface)**: Build CLI/TUI
- Depends on Phase 2 complete
- **Sequential**: Build loader first, then interfaces

**Phase 4 (Features)**: Data generation + verification
- Depends on Phase 2 + 3
- **Parallel**: Synthetic generator and CP-SAT wrapper independent

**Phase 5 (Docs)**: Write documentation
- Depends on Phases 1-4 complete
- Grounded in reality, not speculation

---

## What Agents Do

### Phase 2 Agents (Parallel)

**Agent A (Core Extraction)**:
- Read scheduler_engine.py, statistics.py, tracing.py
- Create core/models.py (Section, ParsedSchedule, Constraints, ScheduleMeta, GeneratedSchedule)
- Create core/parsing.py (parse functions)
- Create core/conflict.py (conflict detection predicates)
- Move tracing.py → core/tracing.py (minimal changes)
- Move statistics.py → core/statistics.py (minimal changes)
- Scope: Extract only; no new logic

**Agent B (Algorithm Refactoring)**:
- Create algorithms/base.py (AlgorithmBase abstract class)
- Refactor scheduler_engine.generate_schedules() → BacktrackingAlgorithm class
- Create algorithms/variation_1/backtracking.py with BacktrackingAlgorithm
- Create algorithms/loader.py (dynamic discovery)
- Scope: Refactor existing logic into new structure

**Agent C (Data Generation)**:
- Move csv_loader.py → data_gen/csv_loader.py (minimal changes, add imports from core/)
- Move config_loader.py → data_gen/config_loader.py (minimal changes)
- Create data_gen/synthetic.py (generate random problems: small/medium/large, loose/tight)
- Scope: Move + enhance

**Agent D (Verification)**:
- Create verification/cpsat_wrapper.py (generic CP-SAT solver)
- Encode same problem structure as backtracking
- Return solution + metadata (runtime, objective, status)
- Scope: Build new module

### Phase 3 Agent (Sequential)

**Agent E (Interface)**:
- Create algorithms/loader.py enhancements (if needed from Phase 2)
- Create interfaces/output.py (format_schedule_table, format_trace, format_json)
- Create interfaces/cli.py (argparse, scriptable mode)
- Create interfaces/tui.py (interactive mode with rich)
- Create main.py (entry point)
- Update test_scheduler.py to use new imports
- Scope: Build interface layer

### Phase 4 Agent (Parallel)

**Agent F (Data Gen Enhancement)** (runs with Phase 3):
- Enhance data_gen/synthetic.py (full implementation)
- Scope: Focused feature

---

## Success Criteria

✓ New directory structure exists and is logical
✓ Code compiles with new imports (no circular dependencies)
✓ Existing tests pass with refactored code
✓ New algorithm added to algorithms/variation_2/ without touching core
✓ CLI mode works: `python3 main.py --algo backtracking_v1 --input data.csv --format json`
✓ TUI mode works: `python3 main.py --interactive`
✓ CP-SAT verification compares backtracking vs. optimal
✓ Documentation reflects actual structure, not aspirational

---

## Estimated Work

- Phase 1: 0.5 days (create directories)
- Phase 2: 2-3 days (4 agents in parallel, 1-2 days each)
- Phase 3: 1.5-2 days (sequential interface building)
- Phase 4: 0.5-1 day (data gen + verification)
- Phase 5: 1 day (documentation)

**Total**: 5-7 days of actual work, compressed via parallelization.

---

**Next Step**: Approve structure, assign agents to Phase 2, then report findings before Phase 3.

