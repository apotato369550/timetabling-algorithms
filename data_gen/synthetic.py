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
import json
from typing import Dict, List, Tuple
from pathlib import Path
from core.models import Section
from core.parsing import parse_schedule_string


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

            # Build schedule string with correct AM/PM handling
            start_ampm = "AM" if start_hour < 12 else "PM"
            end_ampm = "AM" if end_hour < 12 else "PM"

            # Convert to 12-hour format
            start_12h = start_hour if start_hour <= 12 else start_hour - 12
            end_12h = end_hour if end_hour <= 12 else end_hour - 12

            schedule = f"{day_pattern} {start_12h:02d}:00 {start_ampm} - {end_12h:02d}:00 {end_ampm}"

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
        seed: Optional random seed for reproducibility

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


def get_problem_stats(problem: Dict[str, List[Section]]) -> Dict:
    """
    Calculate statistics about a problem instance.

    Args:
        problem: Dictionary mapping course names to lists of Section objects

    Returns:
        Dictionary containing:
        - total_courses: Number of courses
        - total_sections: Total sections across all courses
        - avg_sections_per_course: Average sections per course (float)
        - time_range_coverage: Set of hours covered by any section

    Example:
        stats = get_problem_stats(problem)
        print(f"Courses: {stats['total_courses']}")
        print(f"Sections: {stats['total_sections']}")
    """
    total_courses = len(problem)
    total_sections = sum(len(sections) for sections in problem.values())
    avg_sections = total_sections / total_courses if total_courses > 0 else 0

    # Collect all hours from all sections
    hours_covered = set()
    for sections in problem.values():
        for section in sections:
            parsed = parse_schedule_string(section.schedule)
            if parsed:
                start_hour = parsed['startTime'] // 60
                end_hour = parsed['endTime'] // 60
                hours_covered.update(range(start_hour, end_hour + 1))

    return {
        'total_courses': total_courses,
        'total_sections': total_sections,
        'avg_sections_per_course': avg_sections,
        'time_range_coverage': sorted(list(hours_covered))
    }


def save_problem(problem: Dict[str, List[Section]], filepath: str) -> None:
    """
    Serialize problem instance to JSON file.

    Args:
        problem: Dictionary mapping course names to lists of Section objects
        filepath: Output file path

    Example:
        save_problem(problem, '/path/to/problem.json')
    """
    path = Path(filepath)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Convert Sections to JSON-serializable dicts
    serializable = {}
    for course_name, sections in problem.items():
        serializable[course_name] = []
        for section in sections:
            section_dict = {
                'group': section.group,
                'schedule': section.schedule,
                'enrolled': section.enrolled,
                'status': section.status,
            }
            # Include parsed schedule if available
            if section.parsed_schedule:
                section_dict['parsed_schedule'] = section.parsed_schedule
            serializable[course_name].append(section_dict)

    with open(filepath, 'w') as f:
        json.dump(serializable, f, indent=2)


def load_problem(filepath: str) -> Dict[str, List[Section]]:
    """
    Deserialize problem instance from JSON file.

    Args:
        filepath: Input file path

    Returns:
        Dictionary mapping course names to lists of Section objects

    Example:
        problem = load_problem('/path/to/problem.json')
    """
    with open(filepath, 'r') as f:
        serialized = json.load(f)

    problem = {}
    for course_name, sections_data in serialized.items():
        problem[course_name] = []
        for section_dict in sections_data:
            # Reconstruct Section object
            parsed_schedule = section_dict.get('parsed_schedule')
            section = Section(
                group=section_dict['group'],
                schedule=section_dict['schedule'],
                enrolled=section_dict['enrolled'],
                status=section_dict['status'],
                parsed_schedule=parsed_schedule
            )
            problem[course_name].append(section)

    return problem


def validate_problem(problem: Dict[str, List[Section]]) -> Tuple[bool, List[str]]:
    """
    Validate problem instance for correctness.

    Args:
        problem: Dictionary mapping course names to lists of Section objects

    Returns:
        Tuple (is_valid, errors) where:
        - is_valid: True if all checks pass
        - errors: List of error messages (empty if valid)

    Checks:
    - All courses have at least one section
    - All schedule strings parse correctly
    - All required Section fields are present

    Example:
        is_valid, errors = validate_problem(problem)
        if not is_valid:
            for error in errors:
                print(f"ERROR: {error}")
    """
    errors = []

    # Check problem is not empty
    if not problem:
        errors.append("Problem contains no courses")
        return (False, errors)

    for course_name, sections in problem.items():
        # Check each course has at least one section
        if not sections:
            errors.append(f"Course '{course_name}' has no sections")

        for i, section in enumerate(sections):
            # Check required fields exist
            if not hasattr(section, 'group'):
                errors.append(f"Course '{course_name}' section {i}: missing 'group'")
            if not hasattr(section, 'schedule'):
                errors.append(f"Course '{course_name}' section {i}: missing 'schedule'")
            if not hasattr(section, 'enrolled'):
                errors.append(f"Course '{course_name}' section {i}: missing 'enrolled'")
            if not hasattr(section, 'status'):
                errors.append(f"Course '{course_name}' section {i}: missing 'status'")

            # Check schedule string parses
            if hasattr(section, 'schedule'):
                parsed = parse_schedule_string(section.schedule)
                if parsed is None:
                    errors.append(
                        f"Course '{course_name}' section {i}: "
                        f"schedule '{section.schedule}' failed to parse"
                    )

    return (len(errors) == 0, errors)
