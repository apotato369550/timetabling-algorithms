# Enrollmate Shenanigans - Timetabling Algorithms

## Project Overview

This project contains algorithms for generating class schedules. It is currently focused on a JavaScript implementation of a scheduler engine that generates valid schedules for students based on course sections and constraints.

The core logic resides in `SchedulerEngine.js`, which uses Object-Oriented Programming (OOP) principles to model the scheduling problem.

**Current Functionality:**
*   **Input:** A list of course sections a student wants to enroll in.
*   **Output:** All possible valid schedules that fit specified constraints (e.g., time conflicts, enrollment status).
*   **Algorithm:** Uses recursive backtracking to explore combinations of sections.

**Future Goals:**
*   Convert the existing algorithm to Python.
*   Develop a CLI tool for testing.
*   Extend the algorithm to handle professor/instructor assignment problems (block section scheduling).

## Architecture (`SchedulerEngine.js`)

The codebase is structured using ES6 classes:

*   **`ScheduleParser` (Abstract) & `StandardScheduleParser`:** Parses schedule strings (e.g., "MW 10:00 AM - 11:30 AM") into structured data (days, start time, end time).
*   **`Section`:** Represents a single course section with methods to check validity against constraints (e.g., `isFull`, `isViable`).
*   **`ConflictDetector`:** A utility class to check if two sections have overlapping time slots.
*   **`ScheduleGenerator`:** The core engine that takes a list of sections and constraints, then uses backtracking to find all valid schedule combinations.

## Usage

Currently, `SchedulerEngine.js` is a library file that exports these classes. It is not set up as a standalone executable.

To use it in a JavaScript environment:

```javascript
import { Section, ScheduleGenerator } from './SchedulerEngine.js';

// 1. Define sections
// 2. Define constraints
// 3. Instantiate ScheduleGenerator
// 4. Call generator.generate()
```

## Development Roadmap

1.  **Python Conversion:** Port the logic from `SchedulerEngine.js` to Python.
2.  **CLI Tool:** Create a console application to interface with the algorithm.
3.  **Algorithm Expansion:** Implement logic for professor availability and block section generation.
4.  **Testing:** Create a comprehensive test suite.
