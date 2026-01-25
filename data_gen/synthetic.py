"""
Synthetic Problem Instance Generator

Generates random timetabling problem instances at varying sizes and constraint tightness.
Used for scalability testing and benchmarking of backtracking vs CP-SAT.

Tightness Levels:
- 'loose': 3-5 sections per course (more options, easier to schedule)
- 'tight': 2 sections per course (fewer options, more constraints)

Size Levels:
- 'small': 5 courses
- 'medium': 20 courses
- 'large': 50 courses
"""

import random
from typing import Dict, List, Tuple
from core.models import Section


def generate_problem(
    size: str,
    tightness: str,
    seed: int = None
) -> Dict[str, List[Section]]:
    """
    Generate synthetic problem instance with random courses and sections.

    Args:
        size: 'small' (5), 'medium' (20), or 'large' (50) courses
        tightness: 'loose' (3-5 sections/course) or 'tight' (2 sections/course)
        seed: Optional random seed for reproducibility

    Returns:
        Dictionary mapping course names to lists of Section objects
        Example: {
            'COURSE_001': [Section(...), Section(...), Section(...)],
            'COURSE_002': [Section(...), Section(...)],
            ...
        }

    Example:
        problem = generate_problem('small', 'loose', seed=42)
        for course_name, sections in problem.items():
            print(f"{course_name}: {len(sections)} sections")
    """
    if seed is not None:
        random.seed(seed)

    # Determine number of courses
    courses_count = {
        'small': 5,
        'medium': 20,
        'large': 50
    }.get(size, 10)

    # Determine sections per course distribution
    if tightness == 'loose':
        sections_per_course = list(range(3, 6))  # 3-5 sections
    elif tightness == 'tight':
        sections_per_course = [2, 2, 2]  # Mostly 2 sections
    else:
        sections_per_course = [2, 3, 4]  # Default mixed

    problem: Dict[str, List[Section]] = {}
    course_names = [f"COURSE_{i:03d}" for i in range(1, courses_count + 1)]

    for course in course_names:
        num_sections = random.choice(sections_per_course)
        problem[course] = []

        for section_num in range(1, num_sections + 1):
            # Randomly select day pattern
            day_pattern = random.choice(['MW', 'TTh', 'MWF', 'T', 'Th'])

            # Randomly select start hour (8 AM to 3 PM)
            start_hour = random.randint(8, 15)
            end_hour = start_hour + 1  # 1-hour classes

            # Build schedule string
            schedule = f"{day_pattern} {start_hour:02d}:00 AM - {end_hour:02d}:00 AM"

            # Random enrollment (out of 30)
            current_enrolled = random.randint(0, 30)
            enrolled = f"{current_enrolled}/30"

            # Status based on enrollment
            status = "full" if current_enrolled == 30 else "open"

            section = Section(
                group=section_num,
                schedule=schedule,
                enrolled=enrolled,
                status=status
            )
            problem[course].append(section)

    return problem


def generate_problem_batch(
    configs: List[Tuple[str, str]],
    seed: int = None
) -> Dict[str, Dict[str, List[Section]]]:
    """
    Generate multiple problem instances at once.

    Args:
        configs: List of (size, tightness) tuples
        seed: Optional random seed

    Returns:
        Nested dict: {
            'small_loose': {...},
            'medium_tight': {...},
            'large_loose': {...},
            ...
        }

    Example:
        batch = generate_problem_batch([
            ('small', 'loose'),
            ('medium', 'tight'),
            ('large', 'loose')
        ], seed=42)
    """
    problems = {}
    base_seed = seed if seed is not None else random.randint(1, 1000000)

    for i, (size, tightness) in enumerate(configs):
        problem_seed = base_seed + i
        key = f"{size}_{tightness}"
        problems[key] = generate_problem(size, tightness, seed=problem_seed)

    return problems
