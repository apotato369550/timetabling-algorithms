import time
from typing import Dict, Any


class Statistics:
    """Collects metrics about the scheduling algorithm execution."""

    def __init__(self):
        self.nodes_explored = 0
        self.valid_schedules = 0
        self.pruned_by_conflict = 0
        self.pruned_by_viability = 0
        self.pruned_by_full = 0
        self.start_time = time.time()

    def increment_node(self):
        """Increment the count of nodes explored during backtracking."""
        self.nodes_explored += 1

    def increment_valid_schedules(self):
        """Increment the count of valid schedules found."""
        self.valid_schedules += 1

    def increment_pruned_conflict(self):
        """Increment the count of sections pruned due to time conflicts."""
        self.pruned_by_conflict += 1

    def increment_pruned_viability(self):
        """Increment the count of sections pruned due to viability constraints."""
        self.pruned_by_viability += 1

    def increment_pruned_full(self):
        """Increment the count of sections pruned due to full schedule limit."""
        self.pruned_by_full += 1

    def get_stats(self) -> Dict[str, Any]:
        """Return the collected statistics as a dictionary."""
        execution_time_ms = (time.time() - self.start_time) * 1000
        return {
            'nodes_explored': self.nodes_explored,
            'valid_schedules': self.valid_schedules,
            'pruned_by_conflict': self.pruned_by_conflict,
            'pruned_by_viability': self.pruned_by_viability,
            'pruned_by_full': self.pruned_by_full,
            'execution_time_ms': execution_time_ms
        }
