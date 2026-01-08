# Context: Backtracking + Heuristics + CP-SAT Verification

This directory contains experimental plans for 4 variations of the block section scheduling problem. These plans are designed as **scaffolding and exploration frameworks** for implementing and comparing different algorithmic approaches.

## Research Vision: A Multi-Paradigm Approach

Rather than relying solely on **Google OR-Tools CP-SAT**, this research explores **multiple algorithmic paradigms** to understand their tradeoffs:

1. **Primary: Backtracking with Heuristics**
   - Recursive search through the solution space with intelligent pruning
   - Heuristics guide decision-making (constraint ordering, forward checking, etc.)
   - Finds multiple feasible solutions efficiently
   - Goal: Explore the solution space broadly and find "good enough" solutions quickly

2. **Innovation: Heuristics Exploration**
   - Most-Constrained-First (MCF): prioritize subjects/assignments with fewest options
   - Forward Checking: detect infeasibility early by checking remaining domains
   - Minimum Remaining Values (MRV): choose the variable with fewest valid assignments
   - Arc Consistency: prune inconsistent values from domains
   - Constraint Ordering: solve high-impact constraints first

3. **Verification: CP-SAT as a Verification Tool**
   - After finding solutions via backtracking, encode the problem in CP-SAT
   - Use CP-SAT to verify feasibility bounds and optimality
   - Compare heuristic solutions against CP-SAT's optimal solutions
   - Answer research questions: "How close are our heuristic solutions to optimal?"

### Core Implementation Workflow

1. **Backtracking Framework**: Implement recursive search with decision points
2. **Constraint Enforcement**: Hard constraints (no overlaps, no professor conflicts)
3. **Heuristic Selection**: Choose which variable/value to explore next
4. **Early Termination**: Stop when good solutions found or bounds established
5. **CP-SAT Verification**: Model the same problem in CP-SAT to benchmark
6. **Analysis**: Compare solution quality, runtime, and scalability across approaches

## Research Goals

This project investigates:
- **Feasibility vs. Optimality**: Can fast heuristics find feasible solutions? How optimal are they?
- **Scalability**: How do backtracking + heuristics scale vs. pure CP-SAT on large problems?
- **Heuristic Effectiveness**: Which heuristics work best for different problem variations?
- **Practical Applications**: When should practitioners use backtracking vs. CP-SAT?

## Testing Scaffolding

Each variation should include comprehensive testing:
- **Consistency Tests**: Verify conflict detection and constraint logic
- **Feasibility Tests**: Ensure solutions satisfy hard constraints
- **Optimality Tests**: Compare backtracking solutions against CP-SAT bounds
- **Performance Benchmarks**: Runtime, memory usage, solution quality across problem sizes
- **Scalability Analysis**: How does performance degrade with problem size?

## Documentation Structure

Each variation includes:
- **Problem Statement**: The scheduling challenge being solved
- **Backtracking Pseudocode**: Recursive algorithm with decision points
- **Key Heuristics**: Candidate heuristics to explore (MCF, forward checking, etc.)
- **Complexity Analysis**: Time and space complexity bounds
- **CP-SAT Verification**: How to model the same problem for comparison
- **Research Notes**: Why this variation is interesting and what it teaches

---

> [!NOTE]
> These variations form a progression from simple (schedule generation) to complex (resource-constrained). Each builds on lessons from the previous.
