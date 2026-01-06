# Variation 2: Professor-to-Schedule Assignment

**Problem Statement**: The schedules are already fixed. The goal is to assign professors to these schedules while minimizing unassigned subjects and maximizing professor availability/preference.

## Scaffolding Approach

### The Model
- **Assignment Variable**: For each `(professor, section)` pair, create a Boolean variable `a[prof][section]`.
- **Constraint**: Each `section` must have at most 1 `professor`.
- **Constraint**: Each `professor` can teach only one `section` at any given time (check for overlaps in the fixed schedules).

### CP-SAT Integration Hints
- **Objective Function**: Maximize $(\sum a[prof][section] \times \text{AvailabilityScore}(prof, section)) - (\text{Penalty} \times \text{UnassignedSections})$.
- **Capability Check**: If `prof` is not capable of teaching `section.subject`, force `a[prof][section] = 0`.
- **Availability Score**: Use a weighted integer score based on the professor's preferred time slots.

## Complexity Analysis

### Time Complexity
- **Matching Problem**: This is effectively a variation of the **Generalized Assignment Problem (GAP)**.
- **Search Space**: $O(2^{(P \times S)})$, where $P$ is professors and $S$ is fixed sections. Since schedules are fixed, the overlap constraints drastically prune the tree.
- **Solver Efficiency**: $O(N^3)$ or better for basic matching, but CP-SAT's overhead adds constant factors for more complex preferences.

### Space Complexity
- **Variable Storage**: $O(P \times S)$.
- **Constraint Storage**: $O(P + S + \text{Overlaps})$. Overlaps are pre-calculated.

---

> [!IMPORTANT]
> This variation assumes the "Hardest" part (scheduling) is done. The challenge here is the "Optimal Match" between human preferences and rigid time slots.
