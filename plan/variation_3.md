# Variation 3: Integrated Generation and Assignment

**Problem Statement**: Neither the schedules nor the assignments are fixed. Generate schedules and assign professors simultaneously, maximizing curriculum fulfillment and professor availability.

## Scaffolding Approach

### The Model
- **Coupled Variables**: Create variables for `s[subject][block][time_slot]` (schedule) and `a[prof][subject][block][time_slot]` (assignment).
- **Logical Link**: `a[prof][subject][block][time_slot]` can only be true if `s[subject][block][time_slot]` is also true.
- **Mutual Exclusion**: For a given `(subject, block, time_slot)`, only one `prof` can be assigned.

### CP-SAT Integration Hints
- **Constraint Multiplication**: Instead of Booleans, you might use a single Integer variable `x[subject][block][time_slot]` where the value represents the `ProfID` (0 for unassigned).
- **Implication Constraints**: `model.Add(a_assignment == 1).OnlyEnforceIf(s_schedule)`.
- **Complexity Management**: This integrated approach is significantly more complex because the search space for schedules and assignments is multiplied.

## Complexity Analysis

### Time Complexity
- **Co-Optimization**: $O(2^{(S \times B \times T \times P)})$. This is the most computationally expensive variant so far.
- **Search Strategy**: Use **Branch and Bound**. Finding any valid schedule/assignment is hard; finding an optimal one is much harder.
- **Pruning**: Exploiting the fact that many professors cannot teach many subjects is critical for pruning.

### Space Complexity
- **Variable Storage**: $O(S \times B \times T \times P)$ if using individual Booleans, or $O(S \times B \times T)$ if using an Integer variable for assignments.
- **Memory Overhead**: Significant due to the number of reified constraints (Literal implications).

---

> [!CAUTION]
> Without strong heuristics, the solver might struggle to find an `OPTIMAL` solution in a reasonable time. Aim for `FEASIBLE` first.
