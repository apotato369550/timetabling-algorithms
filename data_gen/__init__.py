"""
Data Generation Module

Provides utilities for loading and generating timetabling problem instances.

- csv_loader: Load courses from CSV files
- config_loader: Load constraint configurations from YAML/JSON
- synthetic: Generate random problem instances at various sizes and tightness levels
"""

from .synthetic import (
    generate_problem,
    generate_problem_batch,
    get_problem_stats,
    save_problem,
    load_problem,
    validate_problem
)
from .csv_loader import load_csv, load_csv_flat, load_csv_real_data, auto_detect_format
from .config_loader import load_config, load_config_with_defaults

__all__ = [
    'generate_problem',
    'generate_problem_batch',
    'get_problem_stats',
    'save_problem',
    'load_problem',
    'validate_problem',
    'load_csv',
    'load_csv_flat',
    'load_csv_real_data',
    'auto_detect_format',
    'load_config',
    'load_config_with_defaults',
]
