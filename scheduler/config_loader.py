"""
Config Loader for Timetabling Scheduler

Parses YAML constraint configuration files and returns typed Constraints dict.
Gracefully falls back to JSON if YAML is not available.
"""

try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False

import json
from typing import Dict, Any, Optional
from scheduler.scheduler_engine import Constraints


def load_config(filepath: str) -> Constraints:
    """
    Load scheduler constraints from YAML or JSON configuration file.

    Supports both YAML and JSON formats:
    ```yaml
    constraints:
      earliestStart: "08:00"
      latestEnd: "18:00"
      allowFull: false
      allowAt_risk: true
      maxSchedules: 5
      maxFullPerSchedule: 1
    ```

    Args:
        filepath: Path to YAML or JSON config file

    Returns:
        Constraints TypedDict with validated values

    Raises:
        FileNotFoundError: If config file doesn't exist
        ValueError: If required constraints are missing or invalid
    """
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            # Try YAML first if available, fallback to JSON
            if HAS_YAML:
                data = yaml.safe_load(f)
            else:
                data = json.load(f)

        if not data:
            raise ValueError(f"Config file is empty: {filepath}")

        if 'constraints' not in data:
            raise ValueError(
                f"'constraints' key not found in config file: {filepath}"
            )

        constraints_data = data['constraints']
        if not isinstance(constraints_data, dict):
            raise ValueError(
                f"'constraints' must be a dictionary, got {type(constraints_data)}"
            )

        # Validate required fields
        required_fields = {
            'earliestStart': str,
            'latestEnd': str,
            'allowFull': bool,
            'allowAt_risk': bool,
            'maxSchedules': int,
            'maxFullPerSchedule': int
        }

        constraints: Dict[str, Any] = {}

        for field, expected_type in required_fields.items():
            if field not in constraints_data:
                raise ValueError(
                    f"Missing required constraint '{field}' in config: {filepath}"
                )

            value = constraints_data[field]

            # Type validation
            if not isinstance(value, expected_type):
                raise ValueError(
                    f"Invalid type for constraint '{field}': "
                    f"expected {expected_type.__name__}, got {type(value).__name__}. "
                    f"Value: {value}"
                )

            # Additional validation for specific fields
            if field == 'earliestStart' or field == 'latestEnd':
                if not _is_valid_time_format(value):
                    raise ValueError(
                        f"Invalid time format for '{field}': '{value}'. "
                        f"Expected HH:MM format (e.g., '08:00')"
                    )

            if field == 'maxSchedules' or field == 'maxFullPerSchedule':
                if value < 0:
                    raise ValueError(
                        f"Invalid value for '{field}': {value}. "
                        f"Must be non-negative."
                    )

            constraints[field] = value

        # Cast to Constraints TypedDict
        return Constraints(
            earliestStart=constraints['earliestStart'],
            latestEnd=constraints['latestEnd'],
            allowFull=constraints['allowFull'],
            allowAt_risk=constraints['allowAt_risk'],
            maxSchedules=constraints['maxSchedules'],
            maxFullPerSchedule=constraints['maxFullPerSchedule']
        )

    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found: {filepath}")
    except (ValueError, json.JSONDecodeError) as e:
        raise ValueError(f"Config parsing error in {filepath}: {e}")


def _is_valid_time_format(time_str: str) -> bool:
    """
    Validate time string in HH:MM format.

    Args:
        time_str: Time string to validate

    Returns:
        True if valid HH:MM format, False otherwise
    """
    if not isinstance(time_str, str):
        return False

    parts = time_str.split(':')
    if len(parts) != 2:
        return False

    try:
        hours = int(parts[0])
        minutes = int(parts[1])
        return 0 <= hours <= 23 and 0 <= minutes <= 59
    except ValueError:
        return False


def load_config_with_defaults(filepath: Optional[str] = None) -> Constraints:
    """
    Load scheduler constraints from YAML file, or return defaults if no file specified.

    Defaults:
    - earliestStart: "08:00"
    - latestEnd: "18:00"
    - allowFull: False
    - allowAt_risk: True
    - maxSchedules: 50
    - maxFullPerSchedule: 0

    Args:
        filepath: Path to YAML config file (None to use defaults)

    Returns:
        Constraints TypedDict
    """
    if filepath is None:
        return Constraints(
            earliestStart="08:00",
            latestEnd="18:00",
            allowFull=False,
            allowAt_risk=True,
            maxSchedules=50,
            maxFullPerSchedule=0
        )

    return load_config(filepath)
