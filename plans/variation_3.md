# Variation 3: Integrated Schedule Generation and Professor Assignment

**Problem Statement**: Neither schedules nor professor assignments are fixed. Simultaneously generate non-overlapping course schedules AND assign professors to teach them, while maximizing curriculum fulfillment and professor availability match. This combines the complexity of Variations 1 and 2 into a **co-optimization problem**.

## Backtracking Algorithm

The core algorithm interleaves schedule selection and professor assignment:

```
function generateAndAssignSchedules(subjects, professors, constraints):
    viable_sections = filterViable(subjects, constraints)
    viable_pairs = filterCapable(professors, subjects)

    results = []

    function backtrack(subject_index, current_schedule, current_assignments, assigned_profs):
        if subject_index == len(subjects):
            // Base case: all subjects have schedules and professors
            if scheduleQuality(current_schedule, current_assignments) meets criteria:
                results.append({schedule: current_schedule, assignments: current_assignments})
            return

        if len(results) >= constraints.maxSolutions:
            return  // early termination

        subject = subjects[subject_index]

        // Heuristic 1: Most-Constrained-First on sections
        section_candidates = sortByViability(viable_sections[subject])

        for section in section_candidates:
            // Check hard constraint: no time conflict with current schedule
            if not hasConflict(section, current_schedule):

                // Heuristic 2: Most-Constrained-First on professors
                // Find professors who can teach this subject AND aren't over-assigned
                prof_candidates = sortByPreference(viable_pairs[subject], assigned_profs)

                for prof in prof_candidates:
                    // Check hard constraint: no time overlap for professor
                    if not professorOverlap(prof, section, current_assignments):
                        // Check soft constraint: professor not over-assigned
                        if canAssignMore(prof, constraints):
                            new_schedule = current_schedule + [section]
                            new_assignments = current_assignments + {subject: prof}
                            new_assigned_profs = assigned_profs + {prof}

                            // Forward checking: can remaining subjects be satisfied?
                            if canExtendCombined(new_schedule, new_assignments,
                                                subjects[subject_index+1:], viable_sections, viable_pairs):
                                backtrack(subject_index + 1, new_schedule, new_assignments, new_assigned_profs)

                // Option: leave subject unassigned (if allowed)
                if constraints.allowUnassigned:
                    backtrack(subject_index + 1, current_schedule, current_assignments, assigned_profs)

    backtrack(0, [], {}, set())
    return results
```

**Decision Points**:
- Which section to select for each subject (guided by availability)
- Which professor to assign to teach that section (guided by preference)
- Whether to leave a subject unscheduled (with penalty)
- Early termination when good solutions found

## Key Heuristics to Explore

1. **Most-Constrained-First (MCF) - Hybrid**
   - Order subjects by fewest viable section + professor pair combinations
   - Process subjects with fewest options first
   - Rationale: Constrain the hardest decisions early

2. **Forward Checking (Co-Optimization Version)**
   - After selecting section + professor for a subject, check if all remaining subjects can still be satisfied
   - Consider both schedule conflicts AND professor assignment conflicts
   - Rationale: Detect infeasibility early from either dimension

3. **Schedule Quality + Professor Preference Ordering**
   - Within each subject, try (section, professor) pairs ordered by combined score
   - Prefer "good" schedules with available professors
   - Rationale: Find high-quality solutions early for pruning

4. **Constraint Propagation: Capability + Availability**
   - Pre-process: remove (section, professor) pairs where professor can't teach subject
   - Remove (section, professor) pairs where times overlap with professor's other assignments
   - Rationale: Reduce search space before search begins

5. **Backtracking with Timeout**
   - Set time limit for backtracking exploration
   - Return best solution found so far when timeout reached
   - Rationale: In co-optimization, perfect solution may not exist in reasonable time

## Complexity Analysis

### Time Complexity
- **Naive Search Space**: $O(2^{(S \times B \times T \times P)})$ where $S$ subjects, $T$ time slots, $P$ professors
- **Practical Search Space**: Much smaller due to capability filtering and conflict constraints
- **Worst Case**: Exponential in both dimensions (schedule selection AND professor assignment)
- **With Strong Heuristics**: Exponential pruning may find solutions quickly, but worst-case remains exponential
- **Typical Case**: $O(\text{backtrack branches} \times \text{constraint checking})$

### Space Complexity
- **Variable Storage**: $O(S \times B \times T \times P)$ for all possible combinations
- **Recursion Stack**: $O(S)$ for call stack depth
- **Current State**: $O(S)$ for current schedule + assignments
- **Result Storage**: $O(R \times S)$ where $R$ = valid solutions found

## CP-SAT Verification

After finding solutions via backtracking, model the combined problem in CP-SAT:

```
model = CpModel()

// Variables for schedule selection: s[subject][section] = 1 if section chosen
s = {}
for subject, section in all_viable_pairs:
    s[subject,section] = model.NewBoolVar(f'subject_{subject}_section_{section}')

// Variables for professor assignment: a[subject][prof] = 1 if prof teaches subject
a = {}
for subject, prof in viable_pairs:
    a[subject,prof] = model.NewBoolVar(f'subject_{subject}_prof_{prof}')

// Constraints: exactly one section per subject
for subject in subjects:
    model.Add(sum(s[subject,sec] for sec in viable_sections[subject]) == 1)

// Constraints: section chosen implies professor assigned to that section
for subject in subjects:
    for sec in viable_sections[subject]:
        for prof in viable_pairs[subject]:
            // If section chosen, professor must be assigned (implication)
            model.Add(s[subject,sec] <= sum(a[subject,prof] for prof in capable_profs[subject]))

// Constraints: no time conflicts between subjects in schedule
for subj_i, subj_j in all_subject_pairs:
    for sec_i in viable_sections[subj_i]:
        for sec_j in viable_sections[subj_j]:
            if hasConflict(sec_i, sec_j):
                model.Add(s[subj_i,sec_i] + s[subj_j,sec_j] <= 1)

// Constraints: professor can't teach overlapping sections
for prof in professors:
    for subj_i, subj_j in all_subject_pairs:
        for sec_i, sec_j in all_section_pairs:
            if hasTimeOverlap(sec_i, sec_j):
                model.Add(a[subj_i,prof] + a[subj_j,prof] <= 1)

// Objective: maximize schedule quality + professor preference
schedule_quality = sum(quality(sec) * s[subj,sec] for subj, sec in all_pairs)
prof_preference = sum(preference(prof) * a[subj,prof] for subj, prof in viable_pairs)
model.Maximize(schedule_quality + prof_preference)

solver = CpSolver()
status = solver.Solve(model)
```

**Verification Questions**:
- Does CP-SAT find the same solution as backtracking?
- What's the optimality gap between backtracking and CP-SAT?
- How much does imposing a time limit hurt solution quality?

## Research Notes

**Why This Variation Matters**:
- Combines two complex problems into one: **Co-optimization is harder than solving sequentially**
- Tests whether heuristics can handle simultaneous constraints across two dimensions
- Realistic scenario: some universities can adjust schedules AND reassign professors
- Foundational for Variation 4 (adds resource constraints)

**Expected Insights**:
- Backtracking with strong heuristics may outperform naive CP-SAT on medium problems (100s of subjects)
- Time limits become critical: perfect solution may not exist in time budget
- Most-Constrained-First heuristic should be very effective here
- Forward checking complexity: checking remaining feasibility is harder with 2D search space

**Expected Challenges**:
- Search space explosion without strong pruning
- Forward checking expensive: must check both schedule + assignment feasibility
- Risk of getting stuck in local optima; need diversification strategies
- Heuristic choice matters more than in simpler variations

**Practical Application**:
- Used when both schedule + professor assignment flexible
- Scheduling committees often use this approach (adjust as constraints change)
- Good testing ground for hybrid approaches (heuristics + local search)
