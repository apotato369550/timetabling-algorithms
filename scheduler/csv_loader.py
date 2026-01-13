"""
CSV Loader for Timetabling Scheduler

Parses course CSV files and returns structured Section objects.
Supports multiple CSV formats with flexible column mapping.
"""

import csv
from typing import List, Optional, Dict, Any
from scheduler.scheduler_engine import Section


def load_csv(
    filepath: str,
    group_col: str = "group",
    schedule_col: str = "schedule",
    enrolled_col: str = "enrolled",
    status_col: str = "status"
) -> List[List[Section]]:
    """
    Load courses from CSV file and return grouped sections.

    Args:
        filepath: Path to CSV file
        group_col: Column name for section group (default: "group")
        schedule_col: Column name for schedule (default: "schedule")
        enrolled_col: Column name for enrollment (default: "enrolled")
        status_col: Column name for status (default: "status")

    Returns:
        List of course groups, where each group is a List[Section]
        Example: [[Section(...), Section(...)], [Section(...)]]
        representing courses with multiple section options

    Raises:
        FileNotFoundError: If CSV file doesn't exist
        ValueError: If required columns are missing
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            if reader.fieldnames is None:
                raise ValueError(f"CSV file is empty: {filepath}")

            # Check for required columns
            required_cols = {group_col, schedule_col, enrolled_col, status_col}
            csv_cols = set(reader.fieldnames)
            missing = required_cols - csv_cols
            if missing:
                raise ValueError(
                    f"Missing required columns in CSV: {missing}. "
                    f"Available columns: {csv_cols}"
                )

            sections_by_course = {}

            for row in reader:
                try:
                    group = int(row[group_col].strip())
                except (ValueError, KeyError):
                    raise ValueError(
                        f"Invalid group value in row: {row}. "
                        f"Column '{group_col}' must contain integers."
                    )

                schedule = row[schedule_col].strip()
                enrolled = row[enrolled_col].strip()
                status = row[status_col].strip()

                if not schedule or not enrolled or not status:
                    raise ValueError(
                        f"Empty required field in row: {row}. "
                        f"schedule, enrolled, and status must not be empty."
                    )

                section = Section(
                    group=group,
                    schedule=schedule,
                    enrolled=enrolled,
                    status=status
                )

                # Group sections by their first two digits of group
                # e.g., group 101 and 102 belong to same course (1xx)
                course_id = group // 100
                if course_id not in sections_by_course:
                    sections_by_course[course_id] = []
                sections_by_course[course_id].append(section)

            if not sections_by_course:
                raise ValueError(f"No valid sections found in CSV: {filepath}")

            # Return sections grouped by course, sorted by course ID
            result = [sections_by_course[cid] for cid in sorted(sections_by_course.keys())]
            return result

    except FileNotFoundError:
        raise FileNotFoundError(f"CSV file not found: {filepath}")
    except csv.Error as e:
        raise ValueError(f"CSV parsing error in {filepath}: {e}")


def load_csv_flat(
    filepath: str,
    group_col: str = "group",
    schedule_col: str = "schedule",
    enrolled_col: str = "enrolled",
    status_col: str = "status"
) -> List[Section]:
    """
    Load courses from CSV file and return flat list of sections.

    Useful when you don't need grouping by course.

    Args:
        filepath: Path to CSV file
        group_col: Column name for section group
        schedule_col: Column name for schedule
        enrolled_col: Column name for enrollment
        status_col: Column name for status

    Returns:
        Flat List[Section] with all sections from CSV
    """
    grouped = load_csv(filepath, group_col, schedule_col, enrolled_col, status_col)
    flat = []
    for group in grouped:
        flat.extend(group)
    return flat


def auto_detect_format(filepath: str) -> str:
    """
    Auto-detect CSV format based on column headers.

    Args:
        filepath: Path to CSV file

    Returns:
        "real" if file has "Course Code" column (real dataset format)
        "simple" if using simple format (group, schedule, enrolled, status)

    Raises:
        FileNotFoundError: If CSV file doesn't exist
        ValueError: If CSV is empty or unreadable
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            if reader.fieldnames is None:
                raise ValueError(f"CSV file is empty: {filepath}")

            csv_cols = set(reader.fieldnames)

            # Check for real format indicator
            if "Course Code" in csv_cols:
                return "real"
            else:
                return "simple"

    except FileNotFoundError:
        raise FileNotFoundError(f"CSV file not found: {filepath}")
    except csv.Error as e:
        raise ValueError(f"CSV parsing error in {filepath}: {e}")


def load_csv_real_data(filepath: str) -> List[List[Section]]:
    """
    Load courses from real dataset CSV format with course metadata.

    Expected columns: Course Code, Course Name, Group, Schedule, Enrolled
    - Enrolled format: "25/30" (current/total)
    - Status inferred: "full" if current==total, else "open"

    Args:
        filepath: Path to CSV file in real format

    Returns:
        List of course groups, where each group is a List[Section]
        Example: [[Section(...), Section(...)], [Section(...)]]
        representing courses with multiple section options

    Raises:
        FileNotFoundError: If CSV file doesn't exist
        ValueError: If required columns missing or format invalid
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)

            if reader.fieldnames is None:
                raise ValueError(f"CSV file is empty: {filepath}")

            # Check for required columns
            required_cols = {"Course Code", "Course Name", "Group", "Schedule", "Enrolled"}
            csv_cols = set(reader.fieldnames)
            missing = required_cols - csv_cols
            if missing:
                raise ValueError(
                    f"Missing required columns in CSV: {missing}. "
                    f"Available columns: {csv_cols}"
                )

            sections_by_course = {}

            for row in reader:
                try:
                    # Parse group as integer
                    group = int(row["Group"].strip())
                except (ValueError, KeyError):
                    raise ValueError(
                        f"Invalid group value in row: {row}. "
                        f"Column 'Group' must contain integers."
                    )

                course_code = row["Course Code"].strip()
                schedule = row["Schedule"].strip()
                enrolled_str = row["Enrolled"].strip()

                if not schedule or not enrolled_str:
                    raise ValueError(
                        f"Empty required field in row: {row}. "
                        f"Schedule and Enrolled must not be empty."
                    )

                # Parse enrolled format: "25/30" -> current=25, total=30
                try:
                    current_str, total_str = enrolled_str.split("/")
                    current = int(current_str.strip())
                    total = int(total_str.strip())
                except (ValueError, AttributeError):
                    raise ValueError(
                        f"Invalid Enrolled format in row: {row}. "
                        f"Expected format: 'current/total' (e.g., '25/30')"
                    )

                # Infer status: "full" if at capacity, else "open"
                status = "full" if current == total else "open"

                # Build enrolled string to maintain compatibility with Section
                enrolled = enrolled_str

                section = Section(
                    group=group,
                    schedule=schedule,
                    enrolled=enrolled,
                    status=status
                )

                # Group sections by their course code
                # e.g., CIS 3100 sections 1, 2, 3 belong to same course
                if course_code not in sections_by_course:
                    sections_by_course[course_code] = []
                sections_by_course[course_code].append(section)

            if not sections_by_course:
                raise ValueError(f"No valid sections found in CSV: {filepath}")

            # Return sections grouped by course, sorted by course ID
            result = [sections_by_course[cid] for cid in sorted(sections_by_course.keys())]
            return result

    except FileNotFoundError:
        raise FileNotFoundError(f"CSV file not found: {filepath}")
    except csv.Error as e:
        raise ValueError(f"CSV parsing error in {filepath}: {e}")
