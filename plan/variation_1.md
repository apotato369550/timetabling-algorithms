# Variation 1: Block Section Generation

**Problem Statement**: Given a set of professors (with specific subjects they can teach and time availabilities) and a curriculum (subjects per course), generate valid block section schedules.

## Scaffolding Approach

### The Model
Think of each "Block Section" as a container that needs to be filled with "Slots". 
- **Slot Variables**: For each subject, each block, and each available time slot, create a Boolean variable: `x[subject][block][time_slot]`.
- **Assignment**: Ensure each subject in the curriculum is assigned exactly once per block.

### CP-SAT Integration Hints
- **No Overlaps**: For any two subjects in the same block, their assigned time slots must not overlap.
- **Professor Availability**: Link subject assignments to professor availability. If no professor is available at `time_slot` for `subject`, then `x[subject][block][time_slot]` must be 0.
- **Global Constraints**: Use `AddNoOverlap` or cumulative constraints if applicable, but standard Boolean exclusion is often simpler for discrete time slots.

## Complexity Analysis

### Time Complexity
- **Constraint Satisfaction**: The search space is approximately $O(2^{(S \times B \times T)})$, where $S$ is subjects, $B$ is blocks, and $T$ is time slots. However, CP-SAT uses pruning and backtracking that significantly reduces this in practice.
- **Solver Efficiency**: $O(\text{Search Nodes} \times \text{Constraint Propagation})$. Propagation is usually linear or $O(N \log N)$ per node.

### Space Complexity
- **Variable Storage**: $O(S \times B \times T)$ to store the Boolean variables.
- **Constraint Storage**: $O(C)$, where $C$ is the number of constraints (overlaps, availability, curriculum requirements).

---

> [!TIP]
> Prioritize modeling the "Time Slot" as an index (e.g., 30-minute intervals) rather than raw timestamps to simplify the constraints.
