# Enrollmate - Timetabling Algorithms

A collection of algorithms and tools for automated course scheduling, originally developed for the Enrollmate ecosystem.

## Project Journey

This repository tracks the development of a robust scheduling engine. The journey began with a JavaScript implementation designed for integration into web applications. Recognizing the need for performance, static analysis, and command-line versatility, the core algorithm was ported to Python.

### Phase 1: The JavaScript Foundation
The initial engine (`SchedulerEngine.js`) established the core logic:
*   **Backtracking Algorithm**: A recursive approach to find all valid schedule combinations.
*   **Conflict Detection**: Intelligent overlap detection handling both days and time ranges.
*   **Constraint Management**: Flexible filtering for full sections, "at-risk" classes, and preferred time windows.

### Phase 2: The Python Port
To support broader data science integration and standalone CLI usage, the logic was ported to `scheduler_engine.py`. This port maintained 1:1 parity with the JS logic while leveraging Python's strong typing (via type hints) and testing ecosystem.

## Core Components

The suite consists of four primary modules:

1.  **ScheduleParser**: Handles the complexity of varied schedule strings (e.g., "MW 10:00 AM - 11:30 AM").
2.  **Section**: Encapsulates course data, enrollment status (full/at-risk), and viability checks.
3.  **ConflictDetector**: A static utility to determine if two sections can exist in the same schedule.
4.  **ScheduleGenerator**: The brain of the project, using backtracking to explore the solution space.

## Getting Started

### Prerequisites
*   Python 3.8+
*   Node.js (optional, for the original JS implementation)

### Running the CLI Tool
The Python implementation includes a CLI tool for rapid testing:
```bash
python3 scheduler_cli.py
```

### Running Tests
Verify the engine's correctness with the built-in test suite:
```bash
python3 test_scheduler.py
```

## Phase 3: Algorithmic Exploration & Research (In Progress)

The project is expanding from a working implementation to a **research investigation** of multiple algorithmic paradigms. Rather than assuming CP-SAT is the optimal approach, we explore tradeoffs between **speed, optimality, and practical applicability**.

### 4 Research Variations (Increasing Complexity)

1. **Variation 1: Schedule Generation**
   - Given subjects and section options, find non-overlapping schedules
   - Constraints: Time conflicts only
   - Complexity: Low (good heuristic testbed)
   - Goal: Can fast heuristics match CP-SAT optimality?

2. **Variation 2: Professor Assignment**
   - Schedules fixed; assign professors optimally
   - Constraints: Professor time conflicts + capability matching
   - Complexity: Medium (bipartite matching problem)
   - Goal: How much do preferences affect performance?

3. **Variation 3: Co-Optimization**
   - Generate schedules AND assign professors simultaneously
   - Constraints: Both schedule + assignment constraints active
   - Complexity: High (exponential in two dimensions)
   - Goal: Can heuristics outperform naive CP-SAT?

4. **Variation 4: Resource-Constrained Scheduling**
   - Schedule + assign + allocate rooms with capacity limits
   - Constraints: All previous plus room availability and professor loads
   - Complexity: Very high (NP-hard RCPSP variant)
   - Goal: What's the practical feasibility vs. optimality tradeoff?

### Algorithmic Approach

**Primary**: Backtracking with intelligent heuristics (Most-Constrained-First, Forward Checking, Arc Consistency)
**Innovation**: Heuristics guide rapid feasible solution discovery
**Verification**: CP-SAT used to benchmark optimality and verify bounds
**Analysis**: Compare solution quality, runtime, scalability across approaches

### Research Goals

- **Feasibility vs. Optimality**: Can fast heuristics find feasible solutions? How close to optimal?
- **Scalability**: How do backtracking + heuristics scale vs. pure CP-SAT?
- **Heuristic Effectiveness**: Which heuristics work best for different problem variations?
- **Practical Guidance**: When should practitioners use each approach?

## Phase 4: Research Documentation & Publication (Planned)

- Performance benchmarks on realistic datasets
- Tradeoff analysis across algorithmic approaches
- Publishable research findings on timetabling heuristics
- Implementation guides and best practices
