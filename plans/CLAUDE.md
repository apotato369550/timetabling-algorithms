# CLAUDE.md: Algorithmic Research Plans

This file explains the research methodology and variation progression for agents implementing the timetabling algorithms research project.

## Research Vision

This project explores **multiple algorithmic paradigms** for solving timetabling problems, with the goal of understanding tradeoffs between **speed, optimality, and practical applicability**.

Rather than assuming CP-SAT is the answer, we investigate:
1. **Backtracking with intelligent heuristics** as the primary solver
2. **CP-SAT as a verification tool** to benchmark optimality
3. **Hybrid approaches** that combine speed and quality
4. **Research questions** about when each paradigm excels

## Variation Progression

The 4 variations form a **complexity gradient**, each building on the previous:

### Variation 1: Schedule Generation (Simplest)
- **Problem**: Given subjects and their section options, find non-overlapping schedules
- **Constraints**: Time conflicts only (no professor or room constraints)
- **Complexity**: Low (good testing ground for heuristics)
- **Key Research Question**: Can forward checking + Most-Constrained-First match CP-SAT's optimality?

### Variation 2: Professor Assignment (Medium)
- **Problem**: Schedules fixed; assign professors to teach them optimally
- **Constraints**: Professor time conflicts, capability matching
- **Complexity**: Medium (bipartite matching with preferences)
- **Key Research Question**: How much does preference optimization affect runtime? What's the optimality gap?

### Variation 3: Co-Optimization (Hard)
- **Problem**: Generate schedules AND assign professors simultaneously
- **Constraints**: Both schedule + assignment constraints active
- **Complexity**: High (exponential in two dimensions)
- **Key Research Question**: Can heuristics outperform naive CP-SAT through smart pruning?

### Variation 4: Resource-Constrained (Hardest)
- **Problem**: Schedule + assign professors + allocate rooms respecting capacity
- **Constraints**: All previous plus room availability and load limits
- **Complexity**: Very high (NP-hard RCPSP variant)
- **Key Research Question**: What's the practical tradeoff between feasibility and optimality?

## Implementation Methodology

### For Each Variation, Implement:

1. **Backtracking Algorithm**
   - Follow pseudocode in variation_X.md
   - Implement decision points and pruning explicitly
   - Measure runtime and solution quality

2. **Heuristics (Pick 2-3 to Compare)**
   - Most-Constrained-First (MCF)
   - Forward Checking
   - One domain-specific heuristic (e.g., room utilization)
   - Compare runtime/quality across variants

3. **CP-SAT Model**
   - Model same problem in CP-SAT (code provided in variation)
   - Run solver and capture status, runtime, objective value
   - Store CP-SAT results for comparison

4. **Comparison Framework**
   - Measure: runtime (ms), solution quality (objective score), optimality gap
   - Create test datasets: small (feasible), medium (challenging), large (extreme)
   - Tabulate results comparing backtracking vs. CP-SAT

5. **Analysis & Documentation**
   - Which heuristics matter most?
   - Where does backtracking beat CP-SAT? Where does CP-SAT win?
   - What problem sizes are practical for each approach?
   - Publish findings in research report

## Testing Strategy

### Test Dataset Categories

1. **Feasibility Tests** (Variation 1-2)
   - Inputs known to have solutions
   - Verify both backtracking and CP-SAT find them
   - Check consistency across runs

2. **Scalability Tests** (All variations)
   - Small: 5-10 subjects, 3-5 professors, 2-3 rooms
   - Medium: 20-30 subjects, 10-15 professors, 5-10 rooms
   - Large: 50+ subjects, 20+ professors, 15+ rooms
   - Measure: runtime, memory, solution quality

3. **Adversarial Tests** (Variation 3-4)
   - Tight constraints (limited professors/rooms)
   - Loose constraints (abundant resources)
   - Measure pruning effectiveness of heuristics

4. **Optimality Tests** (All variations)
   - Compare backtracking solutions to CP-SAT optimal
   - Calculate optimality gap: (CP-SAT optimal - backtracking) / CP-SAT optimal
   - Measure how close heuristics get to optimal

### Expected Results

- **Variation 1**: Backtracking with MCF + forward checking should match CP-SAT on optimality, likely faster
- **Variation 2**: Bipartite matching heuristics effective; CP-SAT likely better for large instances
- **Variation 3**: Heuristics should find feasible solutions fast; optimality gap grows with problem size
- **Variation 4**: Time limits critical; greedy + backtrack hybrid may outperform pure approaches

## Key Insights to Look For

1. **Heuristic Sensitivity**: How much does constraint ordering matter?
2. **Scalability**: Where does backtracking break down? Where does CP-SAT struggle?
3. **Time-Quality Tradeoff**: Can we find "good enough" solutions much faster?
4. **Practical Applicability**: Which approach is best for real-world deployments?

## Connection to Existing Code

The `scheduler/` directory contains the **existing backtracking implementation**:

- **scheduler_engine.py**: Core backtracking algorithm (Variation 1 implementation)
  - Uses recursive backtracking with conflict detection
  - Implements simple filtering (viable sections)
  - Returns multiple valid schedules

This serves as the **foundation** for the research:
- Understand how it works (see scheduler/CLAUDE.md)
- Use it as baseline for Variation 1 comparison
- Extend it for Variations 2-4
- Measure performance against CP-SAT models

## Output & Documentation

For each variation, produce:

1. **Implementation** (Python module)
2. **Tests** (pytest suite with test datasets)
3. **Benchmarks** (runtime/quality measurements)
4. **Analysis** (markdown report comparing approaches)
5. **Research Paper** (journal-style writeup with findings)

## References & Resources

- **Constraint Programming**: Handbook of Constraint Programming (Rossi et al.)
- **Heuristics**: "Algorithms for Constraint Satisfaction Problems" (various)
- **RCPSP**: "The resource-constrained project scheduling problem" (Herroelen et al.)
- **OR-Tools**: Google's CP-SAT documentation

---

**Next Steps**: Pick Variation 1, implement both backtracking (extend existing code) and CP-SAT model, run benchmarks, compare results. Use findings to inform Variation 2 approach.
