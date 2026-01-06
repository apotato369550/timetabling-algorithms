# Context: Advanced Scheduling Scaffolding

This directory contains experimental plans for 4 variations of the block section scheduling problem. These plans are designed as **heuristics and scaffolding** for an agent or model to implement, rather than strict step-by-step instructions.

## Overarching Approach: The CP-SAT Paradigm

All variations should prioritize using **Google OR-Tools CP-SAT** (Constraint Programming - Satisfiability) solver. This is a state-of-the-art combinatorial optimization engine that excels at scheduling problems.

### Core Implementation Workflow
1.  **Model Initialization**: Define the `CpModel`.
2.  **Variable Definiton**: Represent scheduling decisions (e.g., `professor_x_teaches_subject_y_at_time_t`) as Boolean or Integer variables.
3.  **Constraint Enforcement**:
    *   **Hard Constraints**: Non-negotiable (e.g., no room overlaps, no professor conflicts).
    *   **Soft Constraints**: Preferences (e.g., maximize professor availability, minimize gap hours).
4.  **Objective Function**: Define a mathematical expression to maximize (e.g., availability score) or minimize (e.g., unassigned subjects).
5.  **Solver Execution**: Run `CpSolver.Solve(model)` and handle results (`OPTIMAL`, `FEASIBLE`, `INFEASIBLE`).

## Testing Scaffolding

Each variation should be accompanied by a dedicated test suite using `pytest` or `unittest`:
- **Consistency Tests**: Verify that internal logic (e.g., conflict detection) remains correct.
- **Satisfiability Tests**: Ensure the model can find solutions for known-feasible input sets.
- **Optimality Check**: Verify that the solver prefers the higher-ranked availability options.

## CLI & Documentation

The final implementation should reside in a Python package, accessible via a unified CLI. Each variation's documentation should include:
- A detailed explanation of the **Decision Variables** and their domain.
- The mathematical formulation of the **Objective Function**.
- A map of **Constraint Logic** (Hard vs Soft).

---

> [!NOTE]
> Use this context as the foundation for reading the individual variation plans.
