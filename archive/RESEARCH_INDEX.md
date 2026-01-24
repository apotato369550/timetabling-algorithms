# Timetabling Algorithms Research Index

Quick navigation guide for the research documentation and implementation.

## For New Readers

Start here to understand the research vision:

1. **README.md** - Project overview and Phase 3 research roadmap
2. **plans/context.md** - Research methodology and multi-paradigm approach
3. **plans/CLAUDE.md** - Implementation guide for researchers and agents

## For Implementing Variation 1 (Schedule Generation)

1. **scheduler/CLAUDE.md** - Existing implementation documentation
2. **plans/variation_1.md** - Research goals, pseudocode, heuristics, CP-SAT model
3. **scheduler/scheduler_engine.py** - Existing baseline code to extend
4. **test_scheduler.py** - Test suite to validate implementations

## For Implementing Variation 2 (Professor Assignment)

1. **plans/variation_2.md** - Bipartite matching problem formulation
2. **plans/variation_1.md** - Review (foundation for this variation)
3. **plans/CLAUDE.md** - Section on "Connection to Research Variations"

## For Implementing Variation 3 (Co-Optimization)

1. **plans/variation_3.md** - Interleaved scheduling + assignment
2. **plans/variation_1.md** and **variation_2.md** - Review both
3. **plans/CLAUDE.md** - Expected insights and testing strategy

## For Implementing Variation 4 (Resource-Constrained)

1. **plans/variation_4.md** - Full RCPSP variant with rooms
2. **plans/variation_3.md** - Review (foundation for this variation)
3. **plans/CLAUDE.md** - NP-hardness discussion and research potential

## Documentation Structure

```
timetabling-algorithms/
├── README.md                   # Main project overview
├── RESEARCH_INDEX.md           # This file
├── plans/
│   ├── context.md              # Research vision and methodology
│   ├── CLAUDE.md               # Implementation guide for agents
│   ├── variation_1.md          # Schedule generation (simplest)
│   ├── variation_2.md          # Professor assignment (medium)
│   ├── variation_3.md          # Co-optimization (hard)
│   └── variation_4.md          # Resource-constrained (hardest)
├── scheduler/
│   ├── CLAUDE.md               # Existing implementation docs
│   ├── scheduler_engine.py     # Core backtracking algorithm
│   └── block_scheduler.py      # Extended implementation
├── scheduler_cli.py            # Command-line interface
└── test_scheduler.py           # Test suite
```

## Research Methodology

**Goal**: Compare algorithmic paradigms (backtracking + heuristics vs. CP-SAT) across 4 problem variations.

**Approach**:
1. Implement backtracking algorithm with candidate heuristics
2. Model same problem in Google OR-Tools CP-SAT
3. Run benchmarks on test datasets (small, medium, large)
4. Compare: runtime, solution quality, optimality gap
5. Document findings and insights

**Deliverables**:
- Working implementations of Variations 1-4
- Test suites validating correctness
- Benchmark results and analysis
- Research paper with findings

## Key Concepts

### Backtracking with Heuristics
- Recursive search through solution space
- Heuristics guide decision ordering and pruning
- Fast for finding feasible solutions
- Good for exploring solution space broadly

### CP-SAT Verification
- Google's constraint programming solver
- Finds optimal solutions
- Slower but guarantees optimality
- Used to benchmark heuristic solutions

### Heuristics to Explore
1. **Most-Constrained-First (MCF)** - Process most constrained variables first
2. **Forward Checking** - Detect infeasibility early
3. **Arc Consistency** - Prune domains before search
4. **Greedy Initialization** - Quick feasible baseline
5. **Domain-specific** - Room utilization, professor load balancing, etc.

### Problem Variations (Increasing Complexity)
1. **Variation 1**: Schedule generation (no professor constraints)
2. **Variation 2**: Professor assignment (fixed schedules)
3. **Variation 3**: Co-optimization (schedules + assignment together)
4. **Variation 4**: Resource constraints (rooms, capacity, load limits)

## Complexity Progression

| Variation | Problem Type | Complexity | Search Space |
|-----------|-------------|-----------|--------------|
| 1 | Schedule Gen | $O(n_1 \times n_2 \times ... \times n_c)$ | Medium |
| 2 | Assignment | $O(2^{P \times S})$ (with pruning) | Medium-High |
| 3 | Co-Optimization | $O(2^{S \times B \times T \times P})$ | High |
| 4 | RCPSP | $O(2^{S \times B \times T \times P \times R})$ | Very High (NP-hard) |

## Research Questions

### For Variation 1
- Can forward checking + MCF match CP-SAT on optimality?
- How much faster is backtracking than CP-SAT?

### For Variation 2
- How much do professor preferences affect runtime?
- What's the optimality gap between heuristics and CP-SAT?

### For Variation 3
- Can heuristics outperform naive CP-SAT through better pruning?
- Where does co-optimization become intractable?

### For Variation 4
- What's the practical feasibility vs. optimality tradeoff?
- How effective are resource-aware heuristics?

## Implementation Checklist

For each variation:
- [ ] Understand problem formulation (read variation_X.md)
- [ ] Implement backtracking algorithm
- [ ] Test basic correctness (small examples)
- [ ] Implement 2-3 candidate heuristics
- [ ] Model in CP-SAT for verification
- [ ] Create test dataset suite (small, medium, large)
- [ ] Run benchmarks and collect data
- [ ] Analyze results and write findings
- [ ] Document implementation and insights

## Key Files by Role

### For Researchers
- **plans/context.md** - Research vision
- **plans/CLAUDE.md** - Methodology
- **plans/variation_X.md** - Individual problem specifications

### For Implementers
- **scheduler/CLAUDE.md** - Implementation guide
- **scheduler/scheduler_engine.py** - Baseline code
- **test_scheduler.py** - Testing patterns

### For Benchmarking
- **plans/CLAUDE.md** - Testing strategy
- **plans/variation_X.md** - Complexity analysis

## Expected Research Contributions

1. **Novel Heuristics for Timetabling**: MCF + forward checking combinations
2. **Systematic Comparison**: Backtracking vs. CP-SAT across problem sizes
3. **Scalability Analysis**: Where does each approach excel?
4. **Practical Guidance**: Which algorithm to use when?
5. **Publishable Results**: Submission-ready findings on scheduling

## Next Steps

1. **Start**: Read README.md and plans/context.md
2. **Understand**: Review plans/CLAUDE.md and scheduler/CLAUDE.md
3. **Pick Task**: Choose Variation 1 as starting point
4. **Implement**: Follow pseudocode in plans/variation_1.md
5. **Extend**: Add heuristics and CP-SAT model
6. **Benchmark**: Run tests and collect data
7. **Analyze**: Compare results and document findings
8. **Move Forward**: Proceed to Variation 2 with insights from Variation 1

---

**Total Documentation**: ~10,000 words of research-grade specifications
**Status**: Research design complete, ready for implementation
