import sys
import os
import argparse

# Ensure the root directory is in sys.path so we can import from scheduler package
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from scheduler.scheduler_engine import Section, generate_schedules, Constraints
from scheduler.block_scheduler import BlockScheduler

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
    schedules = generate_schedules(all_courses, constraints)
    print(f"Found {len(schedules)} valid schedules.\n")

    for i, schedule in enumerate(schedules):
        print(f"Schedule #{i + 1}:")
        for section in schedule['selections']:
            print(f"  - Group {section.group}: {section.schedule}")
        print("-" * 30)

def run_block_scheduler():
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

def main():
    parser = argparse.ArgumentParser(description="Enrollmate Timetabling CLI")
    parser.add_argument("--variation1", action="store_true", help="Run Variation 1: Block Section Generation")
    args = parser.parse_args()

    if args.variation1:
        run_block_scheduler()
    else:
        run_standard_scheduler()

if __name__ == "__main__":
    main()
