# Variation 2: Professor-to-Schedule Assignment

**Problem Statement**: The course schedules are already fixed and non-overlapping. Assign professors to teach these fixed sections while maximizing professor availability match and minimizing unassigned sections. This is a **matching and assignment problem** on top of fixed infrastructure.

## Backtracking Algorithm

The core algorithm is a bipartite matching search that assigns professors to sections:

```
function assignProfessorsToSections(professors, sections, constraints):
    // Filter: only consider (prof, section) pairs where prof can teach subject
    viable_pairs = filterCapable(professors, sections)

    // Build conflict graph: which sections can a prof not teach simultaneously?
    conflict_graph = buildConflictGraph(sections)

    results = []

    function backtrack(section_index, assignments, assigned_profs):
        if section_index == len(sections):
            // Base case: all sections processed
            if assessmentScore(assignments) meets criteria:
                results.append(assignments)
            return

        if len(results) >= constraints.maxAssignments:
            return  // early termination

        section = sections[section_index]

        // Heuristic: try professors in order of availability preference
        candidates = sortByCandidacy(viable_pairs[section])

        for prof in candidates:
            // Hard constraint: prof not already assigned to conflicting section
            if prof not in assigned_profs or no_time_overlap(prof, section, assignments):
                // Soft constraint: check preference score
                new_assignments = assignments + {section: prof}

                // Forward checking: can we still assign remaining sections?
                if canExtendAssignment(new_assignments, sections[section_index+1:], viable_pairs):
                    backtrack(section_index + 1, new_assignments, assigned_profs + {prof})

        // Option: leave section unassigned (if allowed)
        if constraints.allowUnassigned:
            backtrack(section_index + 1, assignments, assigned_profs)

    backtrack(0, {}, set())
    return results
```

**Decision Points**:
- Which professor to assign to each section (guided by availability preference)
- Whether to leave a section unassigned (allowed with penalty)
- Early termination when good assignments found

## Key Heuristics to Explore

1. **Most-Constrained-First (MCF) - Sections Edition**
   - Order sections by number of capable professors (ascending)
   - Process sections with fewer assignment options first
   - Rationale: Assign difficult sections early, avoid conflicts later

2. **Preference-Guided Ordering**
   - Order professors within each section by availability score
   - Try professors with high preference scores first
   - Rationale: Find high-preference assignments early

3. **Forward Checking (Matching Version)**
   - After assigning a professor to a section, check if remaining sections still have capable unassigned professors
   - Prune assignments that lead to unassignable sections
   - Rationale: Detect infeasibility before exploring deep

4. **Arc Consistency (Bipartite Graph Version)**
   - Pre-process to identify sections with only one capable professor
   - Remove that professor from other sections' candidate lists
   - Rationale: Propagate constraints before search

5. **Greedy Initialization**
   - Start with greedy assignment (professor to highest-preference section)
   - Use as lower bound to prune poor branches
   - Rationale: Quick initial solution enables aggressive pruning

## Complexity Analysis

### Time Complexity
- **Naive Search Space**: $O(2^{(P \times S)})$ where $P$ professors, $S$ sections
- **With Capability Filtering**: Candidates per section typically much smaller than $P$
- **Typical Case**: $O(S \times A^S)$ where $A$ = average capable professors per section
- **With Forward Checking**: Exponential growth halted early when infeasibility detected
- **Greedy + Backtrack Hybrid**: $O(\text{greedy}) + O(\text{backtrack refinement})$

### Space Complexity
- **Variable Storage**: $O(P \times S)$ for assignment variables
- **Conflict Graph**: $O(S^2)$ to store section-section incompatibilities
- **Recursion Stack**: $O(S)$ for call stack depth
- **Result Storage**: $O(A \times S)$ where $A$ = valid assignments stored

## CP-SAT Verification

After finding assignments via backtracking, model as a weighted bipartite matching:

```
model = CpModel()

// Variables: a[prof][section] = 1 if prof teaches section
a = {}
for prof, sec in viable_pairs:
    a[prof,sec] = model.NewBoolVar(f'prof_{prof}_teaches_{sec}')

// Constraints: each section has at most one professor
for sec in sections:
    model.Add(sum(a[prof,sec] for prof if (prof,sec) in viable_pairs) <= 1)

// Constraints: professor can't teach overlapping sections
for prof in professors:
    for sec_i, sec_j in conflicting_sections:
        if (prof,sec_i) in viable_pairs and (prof,sec_j) in viable_pairs:
            model.Add(a[prof,sec_i] + a[prof,sec_j] <= 1)

// Objective: maximize preference score, penalize unassigned sections
preference_score = sum(a[prof,sec] * preference(prof, sec) for prof, sec in viable_pairs)
unassigned_penalty = sum(max_sections - sum(a[prof,sec] for prof in professors))
model.Maximize(preference_score - unassigned_penalty * weight)

solver = CpSolver()
status = solver.Solve(model)
```

**Verification Questions**:
- Does CP-SAT achieve full assignment? (if so, is it feasible?)
- What's the preference score optimality gap?
- Does CP-SAT leave different sections unassigned than backtracking?

## Research Notes

**Why This Variation Matters**:
- Separates scheduling (already done) from assignment (optimization)
- Real-world scenario: university often has fixed schedules, varies professor assignments
- Tests effectiveness of preference optimization vs. pure feasibility

**Expected Insights**:
- Bipartite matching heuristics should work well (polynomial-time matching algorithms exist)
- Forward checking crucial: most infeasibility from capability constraints
- Professor preferences matter: different heuristics yield different satisfaction levels
- How much do heuristics miss vs. CP-SAT's optimal assignment?

**Practical Application**:
- Used after Variation 1 to assign faculty
- Can handle rolling professor availability updates
- Good balance of flexibility and efficiency
