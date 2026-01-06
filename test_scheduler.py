import unittest
from scheduler.scheduler_engine import (
    parse_schedule_string, 
    Section, 
    has_conflict, 
    is_viable,
    generate_schedules, 
    is_full, 
    is_at_risk,
    Constraints
)

class TestFunctionalEngine(unittest.TestCase):

    def test_parse_valid_mw(self):
        result = parse_schedule_string("MW 10:00 AM - 11:30 AM")
        self.assertIsNotNone(result)
        self.assertEqual(result['days'], ['M', 'W'])
        self.assertEqual(result['startTime'], 10 * 60)
        self.assertEqual(result['endTime'], 11 * 60 + 30)

    def test_parse_valid_tth(self):
        result = parse_schedule_string("TTh 01:00 PM - 03:00 PM")
        self.assertIsNotNone(result)
        self.assertEqual(result['days'], ['T', 'Th'])
        self.assertEqual(result['startTime'], 13 * 60)
        self.assertEqual(result['endTime'], 15 * 60)

    def test_parse_invalid_format(self):
        self.assertIsNone(parse_schedule_string("Invalid String"))
        self.assertIsNone(parse_schedule_string("MW 10:00 AM"))

    def test_parse_reversed_times(self):
        self.assertIsNone(parse_schedule_string("MW 11:30 AM - 10:00 AM"))

    def test_is_full(self):
        s1 = Section(1, "MW 10:00 AM - 11:30 AM", "30/30", "FULL")
        s2 = Section(2, "MW 10:00 AM - 11:30 AM", "25/30", "OK")
        self.assertTrue(is_full(s1))
        self.assertFalse(is_full(s2))

    def test_is_at_risk(self):
        s1 = Section(1, "MW 10:00 AM - 11:30 AM", "0/30", "AT-RISK")
        s2 = Section(2, "MW 10:00 AM - 11:30 AM", "5/30", "AT-RISK")
        s3 = Section(3, "MW 10:00 AM - 11:30 AM", "15/30", "OK")
        self.assertTrue(is_at_risk(s1))
        self.assertTrue(is_at_risk(s2))
        self.assertFalse(is_at_risk(s3))

    def test_has_conflict_overlapping(self):
        s1 = Section(1, "MW 10:00 AM - 11:30 AM", "15/30", "OK")
        s2 = Section(2, "MW 11:00 AM - 12:30 PM", "15/30", "OK")
        self.assertTrue(has_conflict(s1, s2))

    def test_has_conflict_non_overlapping_time(self):
        s1 = Section(1, "MW 10:00 AM - 11:30 AM", "15/30", "OK")
        s2 = Section(2, "MW 12:00 PM - 01:30 PM", "15/30", "OK")
        self.assertFalse(has_conflict(s1, s2))

    def test_has_conflict_non_overlapping_days(self):
        s1 = Section(1, "MW 10:00 AM - 11:30 AM", "15/30", "OK")
        s2 = Section(2, "TTh 10:00 AM - 11:30 AM", "15/30", "OK")
        self.assertFalse(has_conflict(s1, s2))

    def test_generate_schedules(self):
        constraints: Constraints = {
            'earliestStart': '08:00',
            'latestEnd': '18:00',
            'allowFull': True,
            'allowAt_risk': True,
            'maxSchedules': 10,
            'maxFullPerSchedule': 1
        }
        
        math = [Section(1, "MW 09:00 AM - 10:30 AM", "15/30", "OK")]
        phys = [Section(2, "MW 10:00 AM - 11:30 AM", "15/30", "OK")] # Conflict
        cs = [Section(3, "TTh 09:00 AM - 10:30 AM", "15/30", "OK")]   # OK
        
        # Test conflict
        schedules = generate_schedules([math, phys], constraints)
        self.assertEqual(len(schedules), 0)
        
        # Test valid
        schedules = generate_schedules([math, cs], constraints)
        self.assertEqual(len(schedules), 1)

if __name__ == '__main__':
    unittest.main()
