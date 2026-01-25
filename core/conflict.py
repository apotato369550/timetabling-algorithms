import re
from .models import Section, Constraints
from .parsing import parse_schedule_string, time_to_minutes


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


def has_conflict(s1: Section, s2: Section) -> bool:
    p1 = s1.parsed_schedule or parse_schedule_string(s1.schedule)
    p2 = s2.parsed_schedule or parse_schedule_string(s2.schedule)

    if not p1 or not p2:
        return False

    shared_days = set(p1['days']) & set(p2['days'])
    if not shared_days:
        return False

    return p1['startTime'] < p2['endTime'] and p2['startTime'] < p1['endTime']
