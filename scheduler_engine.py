import re
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any

class ScheduleParser(ABC):
    """
    Abstract base class for schedule parsing functionality.
    """
    
    @abstractmethod
    def parse(self, schedule_string: str) -> Optional[Dict[str, Any]]:
        """
        Parses a schedule string into a structured format.
        """
        pass

    def to_minutes(self, time_str: str) -> int:
        """
        Converts a time string in HH:MM format to minutes from midnight.
        """
        hours, minutes = map(int, time_str.split(':'))
        return hours * 60 + minutes

class StandardScheduleParser(ScheduleParser):
    """
    Standard implementation of ScheduleParser for parsing common schedule formats.
    """
    
    def parse(self, schedule_string: str) -> Optional[Dict[str, Any]]:
        if not schedule_string or not isinstance(schedule_string, str):
            return None

        # Split by space to separate days and time parts
        parts = schedule_string.strip().split()
        if len(parts) < 4:
            return None

        # Extract days (first part) and time range (remaining parts)
        days_part = parts[0]
        time_part = " ".join(parts[1:])

        # Parse days - handle special case for "Th" (Thursday)
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

        # Parse time range "10:00 AM - 11:30 AM"
        time_match = re.search(r'(\d{1,2}:\d{2}\s*[AP]M)\s*-\s*(\d{1,2}:\d{2}\s*[AP]M)', time_part, re.IGNORECASE)
        if not time_match:
            return None

        start_time_str = time_match.group(1)
        end_time_str = time_match.group(2)

        # Convert to 24-hour format and minutes
        start_minutes = self._convert_to_minutes(start_time_str)
        end_minutes = self._convert_to_minutes(end_time_str)

        if start_minutes is None or end_minutes is None or start_minutes >= end_minutes:
            return None

        return {
            'days': days,
            'startTime': start_minutes,
            'endTime': end_minutes
        }

    def _convert_to_minutes(self, time_str: str) -> Optional[int]:
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

class Section:
    """
    Represents a course section with schedule and enrollment information.
    """
    
    def __init__(self, group: int, schedule: str, enrolled: str, status: str):
        self.group = group
        self.schedule = schedule
        self.enrolled = enrolled
        self.status = status
        self._parsed_schedule = None

    def get_parsed_schedule(self) -> Optional[Dict[str, Any]]:
        if self._parsed_schedule is None:
            parser = StandardScheduleParser()
            self._parsed_schedule = parser.parse(self.schedule)
        return self._parsed_schedule

    def is_full(self) -> bool:
        match = re.search(r'(\d+)/(\d+)', self.enrolled)
        if not match:
            return False
        
        current = int(match.group(1))
        total = int(match.group(2))
        return current >= total

    def is_at_risk(self) -> bool:
        match = re.search(r'(\d+)/(\d+)', self.enrolled)
        if not match:
            return False
            
        current = int(match.group(1))
        total = int(match.group(2))
        
        return current == 0 or (total >= 20 and current < 6) or (total >= 10 and current < 2)

    def is_viable(self, constraints: Dict[str, Any]) -> bool:
        parsed = self.get_parsed_schedule()
        if not parsed:
            return False
            
        earliest_minutes = self.to_minutes(constraints['earliestStart'])
        latest_minutes = self.to_minutes(constraints['latestEnd'])
        
        if parsed['startTime'] < earliest_minutes or parsed['endTime'] > latest_minutes:
            return False
            
        if not constraints.get('allowFull', True) and self.is_full():
            return False
            
        if not constraints.get('allowAtRisk', True) and self.is_at_risk():
            return False
            
        return True

    def to_minutes(self, time_str: str) -> int:
        hours, minutes = map(int, time_str.split(':'))
        return hours * 60 + minutes

class ConflictDetector:
    """
    Utility class for detecting schedule conflicts between sections.
    """
    
    @staticmethod
    def has_conflict(section1: Section, section2: Section) -> bool:
        schedule1 = section1.get_parsed_schedule()
        schedule2 = section2.get_parsed_schedule()
        
        if not schedule1 or not schedule2:
            return False
            
        shared_days = [day for day in schedule1['days'] if day in schedule2['days']]
        if not shared_days:
            return False
            
        return schedule1['startTime'] < schedule2['endTime'] and \
               schedule2['startTime'] < schedule1['endTime']

class ScheduleGenerator:
    """
    Main class for generating valid course schedules using backtracking algorithm.
    """
    
    def __init__(self, sections: List[List[Section]], constraints: Dict[str, Any]):
        self.sections = sections
        self.constraints = constraints

    def generate(self) -> List[Dict[str, Any]]:
        results = []
        viable_sections = []
        
        for course_sections in self.sections:
            viable = [s for s in course_sections if s.is_viable(self.constraints)]
            if not viable:
                return []
            viable_sections.append(viable)
            
        self._backtrack(0, [], results, viable_sections)
        
        max_schedules = self.constraints.get('maxSchedules', 50)
        return results[:max_schedules]

    def _backtrack(self, index: int, current: List[Section], results: List[Dict[str, Any]], viable_sections: List[List[Section]]):
        if len(results) >= self.constraints.get('maxSchedules', 50):
            return
            
        if index >= len(self.sections):
            full_count = len([s for s in current if s.is_full()])
            if full_count <= self.constraints.get('maxFullPerSchedule', 1):
                results.append(self._create_schedule_object(list(current)))
            return
            
        for section in viable_sections[index]:
            has_conflict = False
            for selected_section in current:
                if ConflictDetector.has_conflict(section, selected_section):
                    has_conflict = True
                    break
            
            if not has_conflict:
                current.append(section)
                self._backtrack(index + 1, current, results, viable_sections)
                current.pop()

    def _create_schedule_object(self, sections: List[Section]) -> Dict[str, Any]:
        parsed = [s.get_parsed_schedule() for s in sections]
        parsed = [p for p in parsed if p is not None]
        
        full_count = len([s for s in sections if s.is_full()])
        latest_end = max([p['endTime'] for p in parsed]) if parsed else 0
        preferred_end = self.to_minutes(self.constraints['latestEnd'])
        ends_by_preferred = latest_end <= preferred_end
        
        noon_minutes = self.to_minutes('12:00')
        has_late = any([p['startTime'] >= noon_minutes for p in parsed])
        
        return {
            'selections': sections,
            'parsed': parsed,
            'meta': {
                'fullCount': full_count,
                'endsByPreferred': ends_by_preferred,
                'hasLate': has_late,
                'latestEnd': latest_end
            }
        }

    def to_minutes(self, time_str: str) -> int:
        hours, minutes = map(int, time_str.split(':'))
        return hours * 60 + minutes
