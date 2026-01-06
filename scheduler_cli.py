from scheduler_engine import Section, ScheduleGenerator

def main():
    # Define constraints
    constraints = {
        'earliestStart': '08:00',
        'latestEnd': '18:00',
        'allowFull': False,
        'allowAtRisk': True,
        'maxSchedules': 5,
        'maxFullPerSchedule': 0
    }

    # Define some sample sections
    # Course 1: Math
    math_sections = [
        Section(101, "MW 09:00 AM - 10:30 AM", "15/30", "OK"),
        Section(102, "TTh 09:00 AM - 10:30 AM", "25/30", "OK"),
        Section(103, "MW 02:00 PM - 03:30 PM", "30/30", "FULL")
    ]

    # Course 2: Physics
    physics_sections = [
        Section(201, "MW 10:00 AM - 11:30 AM", "10/25", "OK"), # Conflicts with Math 101 (time)
        Section(202, "TTh 11:00 AM - 12:30 PM", "5/25", "OK"),  # Conflicts with Math 102 (time - no, wait TTh 09:00-10:30 vs 11:00-12:30 is OK)
        Section(203, "F 09:00 AM - 12:00 PM", "20/25", "OK")
    ]

    # Course 3: CS
    cs_sections = [
        Section(301, "MW 01:00 PM - 03:00 PM", "20/40", "OK"),
        Section(302, "TTh 01:00 PM - 03:00 PM", "35/40", "OK")
    ]

    all_courses = [math_sections, physics_sections, cs_sections]

    print("--- Generating Schedules ---")
    generator = ScheduleGenerator(all_courses, constraints)
    schedules = generator.generate()

    print(f"Found {len(schedules)} valid schedules.\n")

    for i, schedule in enumerate(schedules):
        print(f"Schedule #{i + 1}:")
        for section in schedule['selections']:
            print(f"  - Group {section.group}: {section.schedule} ({section.enrolled})")
        print(f"  Meta: {schedule['meta']}")
        print("-" * 30)

if __name__ == "__main__":
    main()
