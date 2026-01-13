# UI & Observability Improvement Plan
## Standard Scheduler (scheduler_engine.py)

**Scope**: Improve observability and usability of the existing scheduler for the standard student course scheduling problem.

**Focus**: Making the algorithm's behavior visible and intuitive to understand.

---

## 1. Execution Trace & Debug Output

### 1.1 Decision Tree Tracing (`--trace` flag)
```
Goal: Show the backtracking search tree as it explores
Output Format:
  Step 1: Math Sections (3 viable options)
    [TRY] Math-101 (MW 9-10:30)
      Step 2: Physics Sections (2 viable options)
        [ACCEPT] Physics-201 (MW 10-11:30) ✗ CONFLICT detected
        [ACCEPT] Physics-202 (TTh 9-10:30) ✓ Valid → continue
          Step 3: CS Sections (2 viable options)
            ... (continue recursion)
    [TRY] Math-102 (TTh 9-10:30)
      Step 2: Physics Sections (1 viable option after filtering)
        ... (continue)
    [TRY] Math-103 (rejected by filtering)

Location: Add tracing logic to backtrack() function in scheduler_engine.py
```

### 1.2 Constraint Violation Logging (`--debug` flag)
```
Goal: Show why branches are pruned
Output:
  Pruned [Math-101, Physics-201]: Time conflict detected
    → Math-101: MW 9:00-10:30
    → Physics-201: MW 10:00-11:30
    → Overlap on Monday 10:00-10:30

  Pruned [Math-105, CS-302]: Section is full (30/30)
    → Reason: allowFull=False in constraints

Location: Enhance has_conflict() and is_viable() to provide reasons
```

### 1.3 Search Tree Statistics
```
Metrics to track:
- Total nodes explored: 487
- Valid complete schedules found: 3
- Branches pruned by conflict: 324 (66.5%)
- Branches pruned by viability: 98 (20.1%)
- Branches pruned by full sections: 34 (7.0%)
- Branches pruned by at-risk sections: 31 (6.4%)
- Execution time: 0.024 seconds
- Nodes per second: 20,292
```

---

## 2. Rich Output Formatting

### 2.1 Calendar Table Display
```
Goal: Display schedules as visual timetables
Output Format (using rich.Table):

SCHEDULE #1
┌─────────────────────────────────────────────┐
│ Time      │ Monday   │ Tuesday │ Wednesday │
├─────────────────────────────────────────────┤
│ 09:00-10:30 │ MATH-101 │   -    │ MATH-101  │
│ 10:00-11:30 │ PHYS-202 │ CS-301 │    -      │
│ 11:30-01:00 │   -     │ PHYS-202 │  -      │
└─────────────────────────────────────────────┘

Location: New function format_schedule_as_table() in output module
```

### 2.2 Schedule Metadata Display
```
Schedule Quality Metrics:
- Full sections: 0/3
- At-risk sections: 0/3
- Latest class end: 13:00 (1:00 PM)
- Ends by preferred time: ✓ Yes
- Has afternoon classes: ✓ Yes (1 class)
- Total class hours: 4.5 hours
- Largest gap: 2.0 hours (11:30-13:30)
```

### 2.3 Comparison View (Multiple Schedules)
```
Schedule   │ Full │ Risk │ Latest │ Gap Max │ Quality
-----------|------|------|--------|---------|--------
Schedule A │  0   │  0   │ 5:00PM │ 1.5h   │ ⭐⭐⭐⭐⭐
Schedule B │  0   │  1   │ 4:30PM │ 0.5h   │ ⭐⭐⭐⭐
Schedule C │  1   │  0   │ 6:00PM │ 2.0h   │ ⭐⭐⭐
```

---

## 3. Data Loading & Configuration

### 3.1 CSV Loader
```
Goal: Load course sections from CSV instead of hard-coding
Format:
  group, schedule, enrolled, status
  101, "MW 09:00 AM - 10:30 AM", "15/30", "OK"
  102, "TTh 09:00 AM - 10:30 AM", "25/30", "OK"

Usage:
  scheduler_cli.py --input courses.csv --output results.json

Location: New module scheduler/csv_loader.py
```

### 3.2 Configuration File Support
```
Goal: Define constraints in config file instead of CLI args
Format (YAML):
  constraints:
    earliestStart: "08:00"
    latestEnd: "18:00"
    allowFull: false
    allowAt_risk: true
    maxSchedules: 5
    maxFullPerSchedule: 0

Usage:
  scheduler_cli.py --config config.yaml

Location: New module scheduler/config_loader.py
```

---

## 4. Output Formats

### 4.1 Terminal Output (Default)
```
- Summary statistics
- Calendar table for each schedule
- Schedule metadata
- Recommendations
```

### 4.2 JSON Export (`--format json`)
```
{
  "metadata": {
    "totalExplored": 487,
    "totalFound": 3,
    "executionTime": 0.024
  },
  "schedules": [
    {
      "id": 1,
      "selections": [
        {"group": 101, "schedule": "MW 09:00 AM - 10:30 AM", ...}
      ],
      "quality": {...}
    }
  ]
}
```

### 4.3 HTML Export (`--format html`)
```
Goal: Generate interactive HTML page showing:
- Calendar visualization
- Schedule comparison
- Quality metrics
- Search statistics

Output: schedule_results.html
```

---

## 5. Enhanced Testing

### 5.1 Test Data Sets
```
Location: data/test_cases.csv
Size progression:
- tiny: 2 courses, 2 sections each (1 viable schedule)
- small: 4 courses, 2-3 sections each (6-12 viable schedules)
- medium: 8 courses, 2-4 sections each (variable solutions)
- large: 15+ courses, 3-5 sections each (complex search)

Each with documented expected outcome
```

### 5.2 Performance Benchmarks
```
Benchmark test on each dataset:
- Execution time
- Nodes explored
- Memory usage
- Pruning effectiveness

Location: New file benchmarks.py with pytest benchmarking
```

---

## 6. CLI Enhancement

### 6.1 Current (`scheduler_cli.py`)
```
python3 scheduler_cli.py [--variation1]
→ Only hard-coded examples
```

### 6.2 Improved
```
python3 scheduler_cli.py --input courses.csv \
                         --config config.yaml \
                         --trace \
                         --debug \
                         --format html \
                         --output results.html

Flags:
  --input FILE          Load courses from CSV
  --config FILE         Load constraints from YAML
  --trace              Show decision tree
  --debug              Show constraint violations
  --format {terminal, json, html}
  --output FILE        Write results to file
  --benchmark          Run with timing/statistics
  --limit DEPTH        Limit trace output depth
  --max-schedules N    Override maxSchedules constraint
```
```

---

## 7. Implementation Priority

### Phase 1: Foundation (Week 1)
- [ ] Add `--trace` and `--debug` flags
- [ ] Implement execution statistics collection
- [ ] Create test data sets (tiny, small, medium)

### Phase 2: Output Formatting (Week 2)
- [ ] Implement rich table formatting
- [ ] Add JSON export
- [ ] Add schedule metadata display

### Phase 3: Data Loading (Week 2)
- [ ] CSV loader module
- [ ] YAML config loader
- [ ] Update CLI to use new loaders

### Phase 4: Advanced Output (Week 3)
- [ ] HTML export
- [ ] Benchmark suite
- [ ] Performance analysis tools

### Phase 5: Testing & Documentation (Week 3)
- [ ] Comprehensive test coverage
- [ ] Usage examples
- [ ] Troubleshooting guide

---

## 8. New File Structure

```
timetabling-algorithms/
├── scheduler/
│   ├── __init__.py
│   ├── scheduler_engine.py       (existing, add tracing)
│   ├── csv_loader.py             (NEW)
│   ├── config_loader.py          (NEW)
│   ├── output_formatter.py       (NEW - tables, JSON, HTML)
│   ├── tracing.py                (NEW - decision tree logging)
│   └── statistics.py             (NEW - metrics collection)
├── data/
│   └── test_cases.csv            (NEW - test datasets)
├── scheduler_cli.py              (modify for new flags)
├── test_scheduler.py             (existing, add new tests)
├── benchmarks.py                 (NEW)
├── config_example.yaml           (NEW)
└── UI_OBSERVABILITY_PLAN.md      (this file)
```

---

## 9. Expected Outcomes

### Before
```
$ python3 scheduler_cli.py
Found 3 valid schedules.

Schedule #1:
  - Group 101: MW 09:00 AM - 10:30 AM
  - Group 202: TTh 09:00 AM - 10:30 AM
  ...
```

### After
```
$ python3 scheduler_cli.py --input courses.csv --trace --format html
[Analyzing course options...]
  Viable sections: 3 math + 2 physics + 2 cs = 12 total options
  Constraint filtering: 12 → 8 after viability check
[Starting backtracking search...]
  Nodes explored: 487
  Valid schedules found: 3
  Pruning rate: 93.8%
[Generating output...]
  ✓ Wrote results to schedule_results.html
[Execution complete in 0.024s]

$ cat schedule_results.html
[Interactive page showing 3 schedules with calendar view,
 comparison table, quality metrics, and search statistics]
```

---

## 10. Key Benefits

1. **Intuition Building**: See exactly why schedules are accepted/rejected
2. **Research Analysis**: Metrics show algorithm effectiveness
3. **Practical Use**: Load real data, export to useful formats
4. **Debugging**: Trace output catches logical errors
5. **Comparison**: Multiple schedules shown with quality metrics
6. **Scalability Testing**: Benchmark suite tracks performance
