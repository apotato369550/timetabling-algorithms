# Variation 4: Full Resource-Constrained Scheduling

**Problem Statement**: The ultimate version combining all constraints. Generate schedules, assign professors, allocate rooms, and respect capacity limits. Maximize curriculum fulfillment while respecting professor load requirements and room availability. This is a **Resource-Constrained Project Scheduling Problem (RCPSP)** variant.

## Backtracking Algorithm with Resource Management

The core algorithm extends Variation 3 with room allocation and capacity constraints:

```
function generateSchedulesWithResources(subjects, professors, rooms, constraints):
    viable_sections = filterViable(subjects, constraints)
    viable_pairs = filterCapable(professors, subjects)

    results = []
    best_solution = null
    best_score = -infinity

    function backtrack(subject_index, current_schedule, current_assignments,
                       room_allocations, assigned_profs, room_utilization):
        if subject_index == len(subjects):
            // Base case: all subjects scheduled, assigned, and allocated rooms
            score = assessmentScore(current_schedule, current_assignments, room_allocations)

            if score > best_score:
                best_score = score
                best_solution = {schedule: current_schedule, assignments: current_assignments,
                                rooms: room_allocations}

            if len(results) < constraints.maxSolutions and score >= feasibility_threshold:
                results.append(best_solution)

            return

        // Aggressive early termination for resource problems
        if len(results) >= constraints.maxSolutions:
            return

        subject = subjects[subject_index]

        // Heuristic 1: Most-Constrained-First on (section, professor, room)
        // Prioritize combinations with fewest viable rooms
        section_prof_candidates = sortByResourceViability(
            viable_sections[subject], viable_pairs[subject], rooms, room_utilization
        )

        for (section, prof) in section_prof_candidates:
            // Check hard constraint: no time conflict in schedule
            if hasConflict(section, current_schedule):
                continue

            // Check hard constraint: professor time overlap
            if professorOverlap(prof, section, current_assignments):
                continue

            // Heuristic 2: Room allocation with capacity matching
            // Find rooms that fit student count for this block
            room_candidates = findSuitableRooms(section, rooms, room_utilization)

            if not room_candidates and not constraints.allowUnscheduled:
                // Prune: can't find a room
                continue

            for room in room_candidates:
                // Check hard constraint: room capacity
                if room.capacity < studentCount(section):
                    continue

                // Check hard constraint: room not double-booked
                if isRoomConflict(room, section, room_allocations):
                    continue

                new_schedule = current_schedule + [section]
                new_assignments = current_assignments + {subject: prof}
                new_rooms = room_allocations + {subject: room}
                new_utilization = updateUtilization(room_utilization, room, section)

                // Forward checking: can remaining subjects be satisfied?
                if canExtendWithResources(new_schedule, new_assignments, new_rooms,
                                         subjects[subject_index+1:], viable_sections,
                                         viable_pairs, rooms, new_utilization):

                    backtrack(subject_index + 1, new_schedule, new_assignments,
                             new_rooms, assigned_profs + {prof}, new_utilization)

            // Option: leave subject unscheduled (with penalty)
            if constraints.allowUnscheduled:
                backtrack(subject_index + 1, current_schedule, current_assignments,
                         room_allocations, assigned_profs, room_utilization)

    backtrack(0, [], {}, {}, set(), {})
    return results
```

**Decision Points**:
- Which section to select (from filtered options)
- Which professor to assign (from capable candidates)
- Which room to allocate (from available options)
- Whether to leave subject unscheduled (with penalty)
- Early termination when good solutions found or time limit reached

## Key Heuristics to Explore

1. **Most-Constrained-First (MCF) - Triple Dimension**
   - Order subjects by fewest viable (section, professor, room) combinations
   - Incorporate room capacity into constraint severity
   - Rationale: The more constrained a subject, the more critical it is to place it early

2. **Forward Checking (Resource Version)**
   - After allocation, verify remaining subjects can be scheduled
   - Check 3 dimensions: schedule conflicts, professor capacity, room availability
   - Rationale: Detect infeasibility early in any dimension

3. **Room Utilization Heuristic**
   - Prefer allocating larger sections to larger rooms (avoid wasting capacity)
   - Prefer rooms with minimal scheduling conflicts
   - Rationale: Maximize room availability for future allocations

4. **Professor Load Balancing**
   - Track teaching hours per professor
   - Avoid overloading any single professor early
   - Rationale: Distribute load across faculty to leave flexibility

5. **Deadline-Driven Search with Timeout**
   - Allocate time budget across subjects (more time for highly constrained)
   - Return best feasible solution when timeout reached
   - Rationale: Resource problems are NP-hard; feasibility may require tradeoff with optimality

6. **Greedy + Backtrack Hybrid**
   - Initialize with greedy allocation (quick feasible solution)
   - Use as lower bound for pruning
   - Backtrack to find improvements
   - Rationale: Quick feasible baseline prevents infinite search

## Complexity Analysis

### Time Complexity
- **Naive Search Space**: $O(2^{(S \times B \times T \times P \times R)})$ where $R$ = number of rooms
- **NP-Hard Problem**: This is the **Resource-Constrained Project Scheduling Problem (RCPSP)**, known NP-hard
- **Practical Behavior**: Heavily depends on problem structure
  - Tight resources (limited rooms/professors): exponential even with strong heuristics
  - Loose resources (abundant rooms/professors): polynomial-like pruning
- **Typical Case**: $O(\text{branches pruned by all constraints})$
- **With Time Limit**: Complexity is time-dependent; returns best solution within budget

### Space Complexity
- **Variable Storage**: $O(S \times R)$ for room allocations, $O(S \times P)$ for professor assignments
- **Room Utilization Tracking**: $O(R \times T)$ for time grid per room
- **Recursion Stack**: $O(S)$ for call stack depth
- **Result Storage**: $O(A \times S)$ where $A$ = valid allocations found

## CP-SAT Verification

After finding solutions via backtracking, model the full problem in CP-SAT:

```
model = CpModel()

// Variables for schedule selection: s[subject][section]
s = {}
for subject, section in all_viable_pairs:
    s[subject,section] = model.NewBoolVar(f'subject_{subject}_section_{section}')

// Variables for professor assignment: a[subject][prof]
a = {}
for subject, prof in viable_pairs:
    a[subject,prof] = model.NewBoolVar(f'subject_{subject}_prof_{prof}')

// Variables for room allocation: r[subject][room]
r = {}
for subject, room in all_subject_room_pairs:
    r[subject,room] = model.NewBoolVar(f'subject_{subject}_room_{room}')

// Constraints: exactly one section, professor, and room per subject
for subject in subjects:
    model.Add(sum(s[subject,sec] for sec in viable_sections[subject]) == 1)
    model.Add(sum(a[subject,prof] for prof in viable_pairs[subject]) == 1)
    model.Add(sum(r[subject,room] for room in rooms) == 1)

// Constraints: no schedule conflicts
for subj_i, subj_j in all_subject_pairs:
    for sec_i, sec_j in conflicting_sections:
        model.Add(s[subj_i,sec_i] + s[subj_j,sec_j] <= 1)

// Constraints: professor no overlaps
for prof in professors:
    for subj_i, subj_j in all_subject_pairs:
        for sec_i, sec_j in time_overlapping_sections:
            model.Add(a[subj_i,prof] + a[subj_j,prof] <= 1)

// Constraints: room capacity
for subject in subjects:
    for room in rooms:
        model.Add(studentCount(subject) <= room.capacity).OnlyEnforceIf(r[subject,room])

// Constraints: room no conflicts
for room in rooms:
    for subj_i, subj_j in all_subject_pairs:
        for sec_i, sec_j in time_overlapping_sections:
            model.Add(r[subj_i,room] + r[subj_j,room] <= 1)

// Constraints: professor load requirements
for prof in professors:
    teaching_hours = sum(sectionDuration(subject) * a[subject,prof] for subject in subjects)
    model.Add(teaching_hours >= prof.min_load)
    model.Add(teaching_hours <= prof.max_load)

// Objective: maximize coverage + preferences
schedule_quality = sum(quality(sec) * s[subj,sec] for subj, sec in all_pairs)
prof_preference = sum(preference(prof) * a[subj,prof] for subj, prof in viable_pairs)
room_efficiency = sum(efficiency(room) * r[subj,room] for subj, room in all_pairs)
model.Maximize(schedule_quality + prof_preference + room_efficiency)

solver = CpSolver()
status = solver.Solve(model)
```

**Verification Questions**:
- Does CP-SAT find a feasible solution? (confirms feasibility is possible)
- What's the professor load optimization gap?
- What's the room utilization gap?
- Where do backtracking and CP-SAT solutions diverge?

## Research Notes

**Why This Variation Matters**:
- Final complexity tier: adds physical resource constraints to scheduling + assignment
- Realistic university scenario: room allocations are critical (facilities limited)
- Tests whether heuristics can handle 3+ dimensional co-optimization
- Represents a publishable research contribution (novel heuristic approaches)

**Expected Insights**:
- Resource constraints dramatically increase complexity vs. Variation 3
- Most-Constrained-First becomes critical for avoiding infeasibility
- Time limits essential: optimal solutions may not exist in reasonable time
- Greedy initialization crucial: provides feasible baseline for comparison
- Room utilization heuristics can provide orders of magnitude improvement

**Expected Challenges**:
- Exponential behavior in adversarial cases (no room fits, professors fully loaded)
- Forward checking expensive: must validate across 3 constraint dimensions
- Memory pressure: resource tracking adds state to each recursion level
- Heuristic sensitivity: small changes to constraint ordering cause large runtime differences

**Practical Applications**:
- Real university timetabling (core research domain)
- Departmental scheduling with shared facilities
- Block section scheduling for residential colleges
- Conference scheduling with venue constraints

**Contribution Potential**:
- Novel heuristic approach to RCPSP variant
- Comparison of heuristics vs. CP-SAT on realistic datasets
- Tradeoff analysis: speed vs. optimality for practical use
- Publishable results in scheduling literature
