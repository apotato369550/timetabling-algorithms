from typing import List, Optional, TypedDict
from dataclasses import dataclass


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
