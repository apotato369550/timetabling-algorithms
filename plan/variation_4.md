# Variation 4: Full Resource Constraints (Rooms & Students)

**Problem Statement**: The ultimate version. Professors with availabilities, mandated subjects, a list of usable rooms, and students who need to fill those rooms based on capacity.

## Scaffolding Approach

### The Model
- **The "Tuple" Decision**: The decision variable is now a 5D tensor: `d[subject][block][time_slot][prof][room]`.
- **Room Capacity**: Each `room` has a `capacity`. The number of students in `block` must be $\le$ `room[capacity]`.
- **Mandated Load**: Each professor has a required load (e.g., minimum 12 hours/week).

### CP-SAT Integration Hints
- **Resource Constraints**: Use `model.AddCumulative`. This is perfect for room management if multiple blocks can use "sub-resources" (not typical for block sections, but useful for lab spaces).
- **Load Balance**: `model.Add(sum(teaching_hours) >= mandated_load)`.
- **Interval Variables**: Use `model.NewIntervalVar` to represent classes with durations. This allows the solver to handle start times and end times natively.

## Complexity Analysis

### Time Complexity
- **NP-Hardness**: This is a full-scale **Resource-Constrained Project Scheduling Problem (RCPSP)**.
- **Scale**: Small departments (10 proferrors, 5 rooms) are solvable in seconds. Large universities (1000 professors, 200 rooms) require **decomposition** (solving one department at a time).

### Space Complexity
- **Sparse Variables**: Do not create variables for `(prof, room)` pairs that are geographically or logically impossible.
- **Constraint Graph**: Extremely dense. Expect high memory usage for the propagator state.

---

> [!TIP]
> This is a thesis-level problem. Focus on **Local Search** or **Large Neighborhood Search (LNS)** within CP-SAT to find high-quality solutions quickly.
