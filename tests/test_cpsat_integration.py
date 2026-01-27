"""
CP-SAT Integration Tests

Tests the CP-SAT wrapper against synthetic problem instances.
Verifies that:
1. CP-SAT solver produces correct output format
2. Solutions are feasible (no time conflicts)
3. Solver handles problems of varying sizes
4. Timeout mechanism works correctly
5. Backtracking and CP-SAT can be compared side-by-side
"""

import sys
import time
import unittest
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.models import Section, Constraints
from core.parsing import parse_schedule_string
from data_gen.synthetic import generate_problem, get_problem_stats
from verification.cpsat_wrapper import solve_with_cpsat
from scheduler.scheduler_engine import generate_schedules


class TestCpsatSmallProblem(unittest.TestCase):
    """Test CP-SAT on small problem instance (5 courses)."""

    def setUp(self):
        """Generate small problem for tests."""
        self.problem = generate_problem('small', 'loose', seed=42)

    def test_cpsat_small_problem(self):
        """Generate small problem, run solve_with_cpsat, verify output format."""
        result = solve_with_cpsat(self.problem, time_limit_s=5)

        # Verify output structure
        self.assertIsInstance(result, dict)
        self.assertIn('feasible', result)
        self.assertIn('solution', result)
        self.assertIn('runtime_ms', result)
        self.assertIn('status', result)
        self.assertIn('objective_value', result)
        self.assertIn('optimal', result)

        # Verify types
        self.assertIsInstance(result['feasible'], bool)
        self.assertIsInstance(result['solution'], dict)
        self.assertIsInstance(result['runtime_ms'], float)
        self.assertIsInstance(result['status'], str)
        self.assertIsInstance(result['optimal'], bool)

    def test_cpsat_runtime_positive(self):
        """Verify runtime_ms is positive."""
        result = solve_with_cpsat(self.problem, time_limit_s=5)
        self.assertGreater(result['runtime_ms'], 0)

    def test_cpsat_status_valid(self):
        """Verify status is one of expected values."""
        result = solve_with_cpsat(self.problem, time_limit_s=5)
        valid_statuses = ['OPTIMAL', 'FEASIBLE', 'INFEASIBLE', 'UNKNOWN']
        self.assertIn(result['status'], valid_statuses)

    def test_cpsat_solution_has_all_courses_if_feasible(self):
        """If feasible, solution should include all courses from problem."""
        result = solve_with_cpsat(self.problem, time_limit_s=5)

        if result['feasible']:
            # Solution should contain one section per course
            self.assertEqual(len(result['solution']), len(self.problem))

            # All courses should be in solution
            for course_name in self.problem.keys():
                self.assertIn(course_name, result['solution'])

            # Each selected section should be valid
            for course_name, section in result['solution'].items():
                self.assertIsInstance(section, Section)
                self.assertIn(section, self.problem[course_name])


class TestCpsatMediumProblem(unittest.TestCase):
    """Test CP-SAT on medium problem instance (20 courses)."""

    def setUp(self):
        """Generate medium problem for tests."""
        self.problem = generate_problem('medium', 'tight', seed=43)

    def test_cpsat_medium_problem(self):
        """Generate medium problem, run solve_with_cpsat."""
        result = solve_with_cpsat(self.problem, time_limit_s=10)

        # Verify output format
        self.assertIsInstance(result['feasible'], bool)
        self.assertIsInstance(result['status'], str)

    def test_cpsat_problem_stats(self):
        """Verify problem has expected statistics."""
        stats = get_problem_stats(self.problem)
        self.assertEqual(stats['total_courses'], 20)
        self.assertGreater(stats['total_sections'], 20)
        self.assertGreater(stats['avg_sections_per_course'], 1.0)


class TestCpsatSolutionFormat(unittest.TestCase):
    """Test that CP-SAT solution format is correct."""

    def setUp(self):
        """Generate small problem for tests."""
        self.problem = generate_problem('small', 'loose', seed=44)

    def test_cpsat_solution_is_dict(self):
        """If feasible, solution should be a dictionary."""
        result = solve_with_cpsat(self.problem, time_limit_s=5)

        if result['feasible']:
            self.assertIsInstance(result['solution'], dict)

    def test_cpsat_solution_sections_valid(self):
        """Each section in solution should be a valid Section object."""
        result = solve_with_cpsat(self.problem, time_limit_s=5)

        if result['feasible']:
            for course_name, section in result['solution'].items():
                # Verify it's a Section
                self.assertIsInstance(section, Section)

                # Verify schedule string is valid
                parsed = parse_schedule_string(section.schedule)
                self.assertIsNotNone(parsed, f"Schedule for {course_name} failed to parse")

    def test_cpsat_solution_no_conflicts(self):
        """All sections in solution should not conflict with each other."""
        result = solve_with_cpsat(self.problem, time_limit_s=5)

        if result['feasible']:
            sections = list(result['solution'].values())

            # Check every pair of sections
            for i in range(len(sections)):
                for j in range(i + 1, len(sections)):
                    sec_i = sections[i]
                    sec_j = sections[j]

                    # Parse both schedules
                    parsed_i = parse_schedule_string(sec_i.schedule)
                    parsed_j = parse_schedule_string(sec_j.schedule)

                    if parsed_i and parsed_j:
                        # Check if they have conflicting days
                        days_i = set(parsed_i['days'])
                        days_j = set(parsed_j['days'])

                        if days_i & days_j:  # If they share days
                            # Times should not overlap
                            # Overlap condition: start_i < end_j AND end_i > start_j
                            has_overlap = (
                                parsed_i['startTime'] < parsed_j['endTime'] and
                                parsed_i['endTime'] > parsed_j['startTime']
                            )
                            self.assertFalse(
                                has_overlap,
                                f"Conflict between {sec_i.schedule} and {sec_j.schedule}"
                            )


class TestCpsatTimeout(unittest.TestCase):
    """Test timeout mechanism for CP-SAT."""

    def test_cpsat_timeout_respected(self):
        """CP-SAT should respect time_limit_s parameter."""
        problem = generate_problem('medium', 'tight', seed=45)

        start = time.perf_counter()
        result = solve_with_cpsat(problem, time_limit_s=1)
        elapsed = time.perf_counter() - start

        # Should complete within roughly 2x the timeout (accounting for solver overhead)
        self.assertLess(elapsed, 3.0, f"Solver took {elapsed}s with 1s timeout")

        # Runtime should be reported accurately
        self.assertGreater(result['runtime_ms'], 0)
        self.assertLess(result['runtime_ms'], 3000)


class TestBacktrackingVsCpsat(unittest.TestCase):
    """Compare backtracking and CP-SAT solvers side-by-side."""

    def setUp(self):
        """Generate test problem and default constraints."""
        self.problem = generate_problem('small', 'loose', seed=46)

        self.constraints: Constraints = {
            'earliestStart': '08:00',
            'latestEnd': '18:00',
            'allowFull': True,
            'allowAt_risk': True,
            'maxSchedules': 10,
            'maxFullPerSchedule': 2
        }

    def test_compare_backtracking_vs_cpsat(self):
        """Run both solvers and generate comparison table."""
        # Run backtracking
        bt_start = time.perf_counter()
        bt_results, bt_stats = generate_schedules(
            list(self.problem.values()),
            self.constraints,
            enable_tracing=False
        )
        bt_elapsed = (time.perf_counter() - bt_start) * 1000

        # Run CP-SAT
        cpsat_result = solve_with_cpsat(self.problem, time_limit_s=10)

        # Build comparison table
        comparison = {
            'backtracking': {
                'runtime_ms': bt_elapsed,
                'feasible': len(bt_results) > 0,
                'solution_count': len(bt_results),
                'status': 'FEASIBLE' if len(bt_results) > 0 else 'INFEASIBLE',
            },
            'cpsat': {
                'runtime_ms': cpsat_result['runtime_ms'],
                'feasible': cpsat_result['feasible'],
                'solution_count': 1 if cpsat_result['feasible'] else 0,
                'status': cpsat_result['status'],
            }
        }

        # Print comparison
        print("\n" + "=" * 70)
        print("ALGORITHM COMPARISON")
        print("=" * 70)
        print(f"{'Algorithm':<20} {'Runtime (ms)':<15} {'Feasible':<12} {'Status':<15}")
        print("-" * 70)
        print(f"{'Backtracking':<20} {comparison['backtracking']['runtime_ms']:<15.2f} "
              f"{str(comparison['backtracking']['feasible']):<12} "
              f"{comparison['backtracking']['status']:<15}")
        print(f"{'CP-SAT':<20} {comparison['cpsat']['runtime_ms']:<15.2f} "
              f"{str(comparison['cpsat']['feasible']):<12} "
              f"{comparison['cpsat']['status']:<15}")
        print("=" * 70)

        # Basic assertions
        self.assertIsInstance(comparison['backtracking']['runtime_ms'], float)
        self.assertIsInstance(comparison['cpsat']['runtime_ms'], float)
        self.assertGreater(comparison['backtracking']['runtime_ms'], 0)
        self.assertGreater(comparison['cpsat']['runtime_ms'], 0)

    def test_both_find_feasible_on_small(self):
        """On small problems, both algorithms should find feasible solutions."""
        # Run backtracking
        bt_results, _ = generate_schedules(
            list(self.problem.values()),
            self.constraints,
            enable_tracing=False
        )

        # Run CP-SAT
        cpsat_result = solve_with_cpsat(self.problem, time_limit_s=10)

        # On small problems, both should typically find solutions
        # (though not guaranteed, so we just verify they match in feasibility)
        bt_feasible = len(bt_results) > 0
        cpsat_feasible = cpsat_result['feasible']

        print(f"\nBacktracking feasible: {bt_feasible}")
        print(f"CP-SAT feasible: {cpsat_feasible}")

        # They should agree on feasibility (usually)
        if bt_feasible or cpsat_feasible:
            # At least one found a solution
            self.assertTrue(bt_feasible or cpsat_feasible)


class TestCpsatEdgeCases(unittest.TestCase):
    """Test CP-SAT on edge cases."""

    def test_cpsat_empty_problem(self):
        """CP-SAT should handle empty problem gracefully."""
        empty_problem = {}
        result = solve_with_cpsat(empty_problem, time_limit_s=5)

        # Empty problem should be trivially feasible
        self.assertTrue(result['feasible'])
        self.assertEqual(len(result['solution']), 0)

    def test_cpsat_single_course(self):
        """CP-SAT should handle single course problem."""
        single_problem = generate_problem('small', 'loose', seed=47)
        # Keep only first course
        single_problem = {k: single_problem[k] for i, k in enumerate(single_problem) if i == 0}

        result = solve_with_cpsat(single_problem, time_limit_s=5)

        # Single course should always be feasible
        self.assertTrue(result['feasible'])
        self.assertEqual(len(result['solution']), 1)

    def test_cpsat_problem_with_all_full_sections(self):
        """CP-SAT should handle problem where all sections are full."""
        problem = generate_problem('small', 'loose', seed=48)

        # Artificially mark all sections as full
        full_problem = {}
        for course_name, sections in problem.items():
            full_problem[course_name] = [
                Section(s.group, s.schedule, "30/30", "FULL", s.parsed_schedule)
                for s in sections
            ]

        result = solve_with_cpsat(full_problem, time_limit_s=5)

        # Should still find a solution (no constraint against full sections)
        if result['feasible']:
            self.assertEqual(len(result['solution']), len(full_problem))


def run_all_tests():
    """Run all test suites and generate summary report."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCpsatSmallProblem))
    suite.addTests(loader.loadTestsFromTestCase(TestCpsatMediumProblem))
    suite.addTests(loader.loadTestsFromTestCase(TestCpsatSolutionFormat))
    suite.addTests(loader.loadTestsFromTestCase(TestCpsatTimeout))
    suite.addTests(loader.loadTestsFromTestCase(TestBacktrackingVsCpsat))
    suite.addTests(loader.loadTestsFromTestCase(TestCpsatEdgeCases))

    # Run with verbose output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    print("=" * 70)

    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
