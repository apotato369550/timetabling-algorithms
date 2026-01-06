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

## Future Roadmap
*   Support for professor-specific constraints.
*   Block sectioning logic for departmental use.
*   Optimization for large-scale enrollment data.
