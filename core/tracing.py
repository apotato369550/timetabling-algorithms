from typing import List


class Tracing:
    """Logs decision tree and pruning information during scheduling."""

    def __init__(self, enabled: bool = False):
        self.enabled = enabled
        self.traces: List[str] = []

    def log_try(self, course_idx: int, section):
        """Log an attempt to use a section for a course."""
        if self.enabled:
            self.traces.append(f"[TRY] Course {course_idx}: Group {section.group} - {section.schedule}")

    def log_prune(self, reason: str, detail: str):
        """Log a decision to prune a branch."""
        if self.enabled:
            self.traces.append(f"[PRUNE] {reason}: {detail}")

    def log_backtrack(self, step: int):
        """Log a backtrack event."""
        if self.enabled:
            self.traces.append(f"[BACKTRACK] Step {step}")

    def log_valid_schedule(self, schedule_idx: int):
        """Log the discovery of a valid schedule."""
        if self.enabled:
            self.traces.append(f"[VALID] Schedule {schedule_idx} found")

    def get_trace(self) -> str:
        """Return the full trace as a formatted string."""
        return '\n'.join(self.traces)

    def get_trace_list(self) -> List[str]:
        """Return the trace as a list of entries."""
        return self.traces.copy()

    def clear(self):
        """Clear all trace entries."""
        self.traces.clear()
