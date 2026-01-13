import re
from typing import List, Dict, Optional, Any, TypedDict, Set, Tuple
from dataclasses import dataclass
from scheduler.statistics import Statistics
from scheduler.tracing import Tracing

# --- Types ---

class ParsedSchedule(TypedDict):
    days: List[str]
    startTime: int
    endTime: int

@dataclass(frozen=True)
class Section:
    group: int
    schedule: str
    enrolled: str
    status: str
    parsed_schedule: Optional[ParsedSchedule] = None

class Constraints(TypedDict):
    earliestStart: str
    latestEnd: str
    allowFull: bool
    allowAt_risk: bool
    maxSchedules: int
    maxFullPerSchedule: int

class ScheduleMeta(TypedDict):
    fullCount: int
    endsByPreferred: bool
    hasLate: bool
    latestEnd: int

class GeneratedSchedule(TypedDict):
    selections: List[Section]
    parsed: List[ParsedSchedule]
    meta: ScheduleMeta

# --- Parsing Functions ---

def time_to_minutes(time_str: str) -> int:
    """Converts a time string in HH:MM format to minutes from midnight."""
    hours, minutes = map(int, time_str.split(':'))
    return hours * 60 + minutes

def parse_time_to_minutes(time_str: str) -> Optional[int]:
    """Parses a time string like '10:00 AM' into minutes from midnight."""
    match = re.search(r'(\d{1,2}):(\d{2})\s*([AP]M)', time_str, re.IGNORECASE)
    if not match:
        return None

    hours = int(match.group(1))
    minutes = int(match.group(2))
    ampm = match.group(3).upper()

    if ampm == 'PM' and hours != 12:
        hours += 12
    elif ampm == 'AM' and hours == 12:
        hours = 0

    return hours * 60 + minutes

def parse_schedule_string(schedule_string: str) -> Optional[ParsedSchedule]:
    """Parses a schedule string (e.g., 'MW 10:00 AM - 11:30 AM') into a dictionary."""
    if not schedule_string or not isinstance(schedule_string, str):
        return None

    parts = schedule_string.strip().split()
    if len(parts) < 4:
        return None

    days_part = parts[0]
    time_part = " ".join(parts[1:])

    # Parse days - handle 'Th'
    days = []
    i = 0
    while i < len(days_part):
        day = days_part[i]
        if day == 'T' and i + 1 < len(days_part) and days_part[i+1] == 'h':
            days.append('Th')
            i += 2
        else:
            days.append(day)
            i += 1

    time_match = re.search(r'(\d{1,2}:\d{2}\s*[AP]M)\s*-\s*(\d{1,2}:\d{2}\s*[AP]M)', time_part, re.IGNORECASE)
    if not time_match:
        return None

    start_minutes = parse_time_to_minutes(time_match.group(1))
    end_minutes = parse_time_to_minutes(time_match.group(2))

    if start_minutes is None or end_minutes is None or start_minutes >= end_minutes:
        return None

    return {
        'days': days,
        'startTime': start_minutes,
        'endTime': end_minutes
    }

# --- Section Utility Functions ---

def is_full(section: Section) -> bool:
    match = re.search(r'(\d+)/(\d+)', section.enrolled)
    if not match:
        return False
    current, total = map(int, match.groups())
    return current >= total

def is_at_risk(section: Section) -> bool:
    match = re.search(r'(\d+)/(\d+)', section.enrolled)
    if not match:
        return False
    current, total = map(int, match.groups())
    return current == 0 or (total >= 20 and current < 6) or (total >= 10 and current < 2)

def is_viable(section: Section, constraints: Constraints) -> bool:
    parsed = section.parsed_schedule or parse_schedule_string(section.schedule)
    if not parsed:
        return False

    earliest = time_to_minutes(constraints['earliestStart'])
    latest = time_to_minutes(constraints['latestEnd'])

    if parsed['startTime'] < earliest or parsed['endTime'] > latest:
        return False

    if not constraints.get('allowFull', True) and is_full(section):
        return False

    if not constraints.get('allowAt_risk', True) and is_at_risk(section):
        return False

    return True

# --- Conflict Detection ---

def has_conflict(s1: Section, s2: Section) -> bool:
    p1 = s1.parsed_schedule or parse_schedule_string(s1.schedule)
    p2 = s2.parsed_schedule or parse_schedule_string(s2.schedule)

    if not p1 or not p2:
        return False

    shared_days = set(p1['days']) & set(p2['days'])
    if not shared_days:
        return False

    return p1['startTime'] < p2['endTime'] and p2['startTime'] < p1['endTime']

# --- Generation Functions ---

def create_schedule_object(sections: List[Section], constraints: Constraints) -> GeneratedSchedule:
    parsed_list = [s.parsed_schedule or parse_schedule_string(s.schedule) for s in sections]
    parsed_list = [p for p in parsed_list if p is not None]

    full_count = sum(1 for s in sections if is_full(s))
    latest_end = max((p['endTime'] for p in parsed_list), default=0)
    preferred_end = time_to_minutes(constraints['latestEnd'])
    
    noon_minutes = time_to_minutes('12:00')
    has_late = any(p['startTime'] >= noon_minutes for p in parsed_list)

    return {
        'selections': list(sections),
        'parsed': parsed_list,
        'meta': {
            'fullCount': full_count,
            'endsByPreferred': latest_end <= preferred_end,
            'hasLate': has_late,
            'latestEnd': latest_end
        }
    }

def generate_schedules(
    course_sections: List[List[Section]], 
    constraints: Constraints,
    enable_tracing: bool = False
) -> Tuple[List[GeneratedSchedule], Dict[str, Any]]:
    
    # Initialize instrumentation
    stats = Statistics()
    tracer = Tracing(enabled=enable_tracing)
    
    # Pre-filter viable sections and parse their schedules once
    viable_lists = []
    for course_idx, sections in enumerate(course_sections):
        viable = []
        for s in sections:
            if is_viable(s, constraints):
                parsed = parse_schedule_string(s.schedule)
                # Create a new section object with the parsed schedule attached
                viable.append(Section(s.group, s.schedule, s.enrolled, s.status, parsed))
            else:
                stats.increment_pruned_viability()
                tracer.log_prune("VIABILITY", f"Course {course_idx}: Group {s.group}")
        if not viable:
            return [], stats.get_stats()
        viable_lists.append(viable)

    results = []
    max_schedules = constraints.get('maxSchedules', 50)
    max_full = constraints.get('maxFullPerSchedule', 1)

    def backtrack(step: int, current_selection: List[Section]):
        stats.increment_node()
        
        if len(results) >= max_schedules:
            return

        if step == len(viable_lists):
            full_count = sum(1 for s in current_selection if is_full(s))
            if full_count <= max_full:
                results.append(create_schedule_object(current_selection, constraints))
                stats.increment_valid_schedules()
                tracer.log_valid_schedule(len(results))
            else:
                stats.increment_pruned_full()
                tracer.log_prune("FULL_LIMIT", f"Too many full courses: {full_count} > {max_full}")
            return

        for section in viable_lists[step]:
            tracer.log_try(step, section)
            conflict = any(has_conflict(section, s) for s in current_selection)
            if not conflict:
                backtrack(step + 1, current_selection + [section])
            else:
                stats.increment_pruned_conflict()
                tracer.log_prune("CONFLICT", f"Course {step}: Group {section.group}")

    backtrack(0, [])
    return results, stats.get_stats()
