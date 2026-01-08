# Variation 1: Block Section Schedule Generation

**Problem Statement**: Given a curriculum (set of subjects per course/block) and multiple section options for each subject (with different schedules), generate valid non-overlapping course schedules where no two subjects in the same block have time conflicts.

## Backtracking Algorithm

The core algorithm is a recursive search that builds valid schedules by choosing one section per subject:

```
function generateSchedules(subjects, constraints):
    viable_sections = filterViable(subjects, constraints)
    if any subject has zero viable sections:
        return []  // infeasible

    results = []

    function backtrack(subject_index, current_schedule):
        if subject_index == len(viable_sections):
            // Base case: all subjects assigned
            if scheduleQuality(current_schedule) meets criteria:
                results.append(current_schedule)
            return

        if len(results) >= constraints.maxSchedules:
            return  // early termination

        for section in viable_sections[subject_index]:
            // Check hard constraint: no time conflicts
            if not hasConflict(section, current_schedule):
                // Heuristic pruning: forward checking
                if canExtend(section, viable_sections[subject_index+1:]):
                    backtrack(subject_index + 1, current_schedule + [section])

    backtrack(0, [])
    return results
```

**Decision Points**:
- Which section to try for each subject (guided by heuristics)
- When to prune the search tree (based on constraint violation or bounds)

## Key Heuristics to Explore

1. **Most-Constrained-First (MCF)**
   - Order subjects by number of viable sections (ascending)
   - Process subjects with fewer options first
   - Rationale: Fail early if a constrained subject can't be placed

2. **Forward Checking**
   - After selecting a section, check if remaining subjects still have valid options
   - Eliminate sections that create dead-ends
   - Rationale: Avoid exploring branches that lead to infeasibility

3. **Schedule Quality Ordering**
   - Within a subject, order sections by quality (e.g., preferred time, fewer full spots)
   - Try "good" sections before less desirable ones
   - Rationale: Find high-quality solutions early, allowing earlier pruning

4. **Arc Consistency (Optional)**
   - Pre-process to remove sections that will always conflict
   - Build a conflict graph between sections
   - Rationale: Reduce domain before search begins

## Complexity Analysis

### Time Complexity
- **Naive Search Space**: $O(2^{(S \times B \times T)})$ where $S$ subjects, $B$ blocks, $T$ time slots per subject
- **With Backtracking**: $O(n_1 \times n_2 \times ... \times n_S)$ where $n_i$ = viable sections for subject $i$
- **Typical Case**: Much faster than worst-case due to conflict pruning (most branches eliminated early)
- **Best-Case**: $O(S)$ if forward checking fails immediately or only one solution exists

### Space Complexity
- **Variable Storage**: $O(S \times A)$ where $A$ = average viable sections per subject
- **Recursion Stack**: $O(S)$ for the call stack depth
- **Result Storage**: $O(R \times S)$ where $R$ = number of valid schedules found

## CP-SAT Verification

After finding schedules via backtracking, model the same problem in CP-SAT:

```
model = CpModel()

// Variables: x[i][j] = 1 if section j chosen for subject i
x = {}
for i in subjects:
    for j in viable_sections[i]:
        x[i,j] = model.NewBoolVar(f'subject_{i}_section_{j}')

// Constraints: exactly one section per subject
for i in subjects:
    model.Add(sum(x[i,j] for j in viable_sections[i]) == 1)

// Constraints: no overlaps
for i,j in all_pairs_of_subjects:
    for sec_i in viable_sections[i]:
        for sec_j in viable_sections[j]:
            if hasConflict(sec_i, sec_j):
                model.Add(x[i,sec_i] + x[j,sec_j] <= 1)

// Objective: maximize schedule quality (optional)
model.Maximize(sum(quality_score(j) * x[i,j] for i,j))

solver = CpSolver()
status = solver.Solve(model)
```

**Verification Questions**:
- Does CP-SAT find a solution? (confirms feasibility)
- Are our backtracking solutions among CP-SAT's solutions?
- What's the optimality gap? (difference from CP-SAT's best solution)

## Research Notes

**Why This Variation Matters**:
- Simplest version: no professor assignments, no resource constraints
- Foundation for more complex variations
- Good testing ground for heuristics (impact clearly visible)

**Expected Insights**:
- Forward checking should dramatically reduce search space
- Most-Constrained-First ordering should find solutions faster
- Comparison with CP-SAT shows feasibility bounds
- Can we match CP-SAT's optimality with fast heuristics?

**Practical Application**:
- This is essentially the **Enrollmate course scheduling problem**
- Real students need schedules quickly (not necessarily optimal)
- Backtracking + heuristics likely sufficient for real-world use
