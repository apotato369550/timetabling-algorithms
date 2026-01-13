import sys
import os
import argparse
import json

# Ensure the root directory is in sys.path so we can import from scheduler package
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scheduler.scheduler_engine import Section, generate_schedules, Constraints
from scheduler.csv_loader import load_csv, load_csv_real_data, auto_detect_format
from scheduler.config_loader import load_config_with_defaults

def run_standard_scheduler():
    # Define constraints
    constraints: Constraints = {
        'earliestStart': '08:00',
        'latestEnd': '18:00',
        'allowFull': False,
        'allowAt_risk': True,
        'maxSchedules': 5,
        'maxFullPerSchedule': 0
    }

    # Define some sample sections
    math_sections = [
        Section(101, "MW 09:00 AM - 10:30 AM", "15/30", "OK"),
        Section(102, "TTh 09:00 AM - 10:30 AM", "25/30", "OK")
    ]
    physics_sections = [
        Section(201, "MW 10:00 AM - 11:30 AM", "10/25", "OK"),
        Section(202, "TTh 11:00 AM - 12:30 PM", "5/25", "OK")
    ]
    all_courses = [math_sections, physics_sections]

    print("--- Running Standard Scheduler ---")
    schedules, stats = generate_schedules(all_courses, constraints)
    print(f"Found {len(schedules)} valid schedules.\n")

    for i, schedule in enumerate(schedules):
        print(f"Schedule #{i + 1}:")
        for section in schedule['selections']:
            print(f"  - Group {section.group}: {section.schedule}")
        print("-" * 30)

def run_block_scheduler():
    from scheduler.block_scheduler import BlockScheduler

    print("--- Running Block Scheduler (Variation 1) ---")

    # 1. Define Subjects
    subjects = [
        {'id': 1, 'name': 'Mathematics', 'required_slots': 3},  # 1.5 hours
        {'id': 2, 'name': 'Physics', 'required_slots': 3},
        {'id': 3, 'name': 'Computer Science', 'required_slots': 4} # 2 hours
    ]

    # 2. Define Time Slots (using 30-min intervals)
    # 0: Mon 08:00-08:30, 1: Mon 08:30-09:00, etc.
    time_slots = []
    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
    start_hour = 8
    for d_idx, day in enumerate(days):
        for slot in range(20): # 8 AM to 6 PM (10 hours = 20 slots)
            h = start_hour + (slot // 2)
            m = "00" if slot % 2 == 0 else "30"
            end_h = start_hour + ((slot + 1) // 2)
            end_m = "30" if (slot + 1) % 2 != 0 else "00"
            time_slots.append({
                'id': d_idx * 20 + slot,
                'day': day,
                'start': f"{h:02d}:{m}",
                'end': f"{end_h:02d}:{end_m}"
            })

    # 3. Define Professors
    # Prof 1 can teach Math and Physics, available Mon-Wed morning
    # Prof 2 can teach CS, available all week
    professors = [
        {
            'id': 1, 
            'name': 'Dr. Smith', 
            'qualified_subjects': [1, 2], 
            'availability': list(range(0, 10)) + list(range(20, 30)) + list(range(40, 50))
        },
        {
            'id': 2, 
            'name': 'Dr. Jones', 
            'qualified_subjects': [3], 
            'availability': list(range(100))
        }
    ]

    # 4. Define Blocks
    blocks = [
        {'id': 1, 'name': 'Block A', 'curriculum': [1, 2, 3]},
        {'id': 2, 'name': 'Block B', 'curriculum': [1, 3]}
    ]

    scheduler = BlockScheduler(subjects, professors, blocks, time_slots)
    results = scheduler.solve()

    if results:
        for block_name, schedule in results.items():
            print(f"\nSchedule for {block_name}:")
            # Sort by day and time
            day_order = {'Mon': 0, 'Tue': 1, 'Wed': 2, 'Thu': 3, 'Fri': 4}
            sorted_schedule = sorted(schedule, key=lambda x: (day_order[x['day']], x['start']))
            for slot in sorted_schedule:
                print(f"  {slot['day']} {slot['start']}-{slot['end']}: {slot['subject']}")
    else:
        print("No valid schedule found.")

def format_output(schedules, format_type):
    """
    Format schedule output in requested format.

    Args:
        schedules: List of GeneratedSchedule objects
        format_type: Output format ('terminal', 'json', 'html')

    Returns:
        Formatted string
    """
    if format_type == 'json':
        output = []
        for i, schedule in enumerate(schedules):
            schedule_dict = {
                'schedule_id': i + 1,
                'selections': [
                    {
                        'group': s.group,
                        'schedule': s.schedule,
                        'enrolled': s.enrolled,
                        'status': s.status
                    }
                    for s in schedule['selections']
                ],
                'meta': schedule['meta']
            }
            output.append(schedule_dict)
        return json.dumps(output, indent=2)

    elif format_type == 'html':
        html = '<html><head><meta charset="utf-8"><style>body{font-family:Arial}table{border-collapse:collapse}th,td{border:1px solid black;padding:8px}th{background:#f0f0f0}.meta{background:#f9f9f9}</style></head><body>'
        html += f'<h1>Generated Schedules ({len(schedules)} total)</h1>'
        for i, schedule in enumerate(schedules):
            html += f'<h2>Schedule #{i + 1}</h2>'
            html += '<table><thead><tr><th>Group</th><th>Schedule</th><th>Enrolled</th><th>Status</th></tr></thead><tbody>'
            for s in schedule['selections']:
                html += f'<tr><td>{s.group}</td><td>{s.schedule}</td><td>{s.enrolled}</td><td>{s.status}</td></tr>'
            html += '</tbody></table>'
            meta = schedule['meta']
            html += f'<div class="meta"><p>Full Count: {meta["fullCount"]}, Ends by Preferred: {meta["endsByPreferred"]}, Has Late: {meta["hasLate"]}, Latest End: {meta["latestEnd"]}</p></div>'
        html += '</body></html>'
        return html

    else:  # terminal
        output = f"Found {len(schedules)} valid schedules.\n\n"
        for i, schedule in enumerate(schedules):
            output += f"Schedule #{i + 1}:\n"
            for section in schedule['selections']:
                output += f"  - Group {section.group}: {section.schedule} ({section.enrolled}, {section.status})\n"
            output += "-" * 50 + "\n"
        return output


def run_with_csv_and_config(input_file, config_file, format_type, output_file):
    """
    Run scheduler with CSV input and YAML config.

    Args:
        input_file: Path to CSV file with course sections
        config_file: Path to YAML config file (or None for defaults)
        format_type: Output format ('terminal', 'json', 'html')
        output_file: Output file path (or None for stdout)
    """
    try:
        # Load courses from CSV
        print(f"Loading courses from {input_file}...")

        # Auto-detect CSV format and load accordingly
        detected_format = auto_detect_format(input_file)
        if detected_format == "real":
            print(f"Detected real dataset format, using load_csv_real_data...")
            course_sections = load_csv_real_data(input_file)
        else:
            print(f"Detected simple format, using load_csv...")
            course_sections = load_csv(input_file)

        # Load constraints from config (or use defaults)
        if config_file:
            print(f"Loading constraints from {config_file}...")
            constraints = load_config_with_defaults(config_file)
        else:
            print("Using default constraints...")
            constraints = load_config_with_defaults(None)

        print(f"Loaded {len(course_sections)} courses")

        # Run scheduler
        print("Generating schedules...")
        schedules, stats = generate_schedules(course_sections, constraints)

        # Format output
        output = format_output(schedules, format_type)

        # Write output
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(output)
            print(f"Output written to {output_file}")
        else:
            print(output)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Enrollmate Timetabling CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run standard scheduler with defaults
  python scheduler_cli.py

  # Run with CSV input and config file
  python scheduler_cli.py --input data/test_cases.csv --config config_example.yaml

  # Output to JSON file
  python scheduler_cli.py --input data/test_cases.csv --format json --output results.json

  # Load predefined dataset (e.g., Computer Science)
  python scheduler_cli.py --dataset cs

  # Load dataset with custom config and output to JSON
  python scheduler_cli.py --dataset biology --config config_example.yaml --format json --output results.json

  # Run Block Scheduler variation
  python scheduler_cli.py --variation1
        """
    )

    parser.add_argument(
        "--input",
        type=str,
        help="Path to CSV file with course sections"
    )
    parser.add_argument(
        "--dataset",
        type=str,
        help="Load predefined dataset by name (accounting, cs, biology, engineering, finance, law, physics, psychology) or by filepath to CSV file. Takes precedence over --input if both specified."
    )
    parser.add_argument(
        "--config",
        type=str,
        help="Path to YAML config file with constraints"
    )
    parser.add_argument(
        "--format",
        choices=['terminal', 'json', 'html'],
        default='terminal',
        help="Output format (default: terminal)"
    )
    parser.add_argument(
        "--output",
        type=str,
        help="Output file path (default: stdout)"
    )
    parser.add_argument(
        "--variation1",
        action="store_true",
        help="Run Variation 1: Block Section Generation"
    )

    args = parser.parse_args()

    # Map dataset argument to file path
    dataset_mapping = {
        'accounting': 'data/accounting-student-schedule.csv',
        'cs': 'data/cs-student-schedule.csv',
        'biology': 'data/biology-student-schedule.csv',
        'engineering': 'data/engineering-student-schedule.csv',
        'finance': 'data/finance-student-schedule.csv',
        'law': 'data/law-student-schedule.csv',
        'physics': 'data/physics-student-schedule.csv',
        'psychology': 'data/psychology-student-schedule.csv'
    }

    if args.variation1:
        run_block_scheduler()
    elif args.dataset:
        # --dataset takes precedence: check if it's a predefined name or filepath
        if args.dataset in dataset_mapping:
            input_file = dataset_mapping[args.dataset]
        else:
            # Treat as filepath
            input_file = args.dataset
        run_with_csv_and_config(input_file, args.config, args.format, args.output)
    elif args.input:
        run_with_csv_and_config(args.input, args.config, args.format, args.output)
    else:
        run_standard_scheduler()

if __name__ == "__main__":
    main()
