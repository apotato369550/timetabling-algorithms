import re
from typing import Optional
from .models import ParsedSchedule


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
