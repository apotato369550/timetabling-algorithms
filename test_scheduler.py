import unittest
from scheduler_engine import StandardScheduleParser, Section, ConflictDetector, ScheduleGenerator

class TestStandardScheduleParser(unittest.TestCase):
    def setUp(self):
        self.parser = StandardScheduleParser()

    def test_parse_valid_mw(self):
        result = self.parser.parse("MW 10:00 AM - 11:30 AM")
        self.assertIsNotNone(result)
        self.assertEqual(result['days'], ['M', 'W'])
        self.assertEqual(result['startTime'], 10 * 60)
        self.assertEqual(result['endTime'], 11 * 60 + 30)

    def test_parse_valid_tth(self):
        result = self.parser.parse("TTh 01:00 PM - 03:00 PM")
        self.assertIsNotNone(result)
        self.assertEqual(result['days'], ['T', 'Th'])
        self.assertEqual(result['startTime'], 13 * 60)
        self.assertEqual(result['endTime'], 15 * 60)

    def test_parse_invalid_format(self):
        self.assertIsNone(self.parser.parse("Invalid String"))
        self.assertIsNone(self.parser.parse("MW 10:00 AM"))

    def test_parse_reversed_times(self):
        self.assertIsNone(self.parser.parse("MW 11:30 AM - 10:00 AM"))

class TestSection(unittest.TestCase):
    def test_is_full(self):
        s1 = Section(1, "MW 10:00 AM - 11:30 AM", "30/30", "FULL")
        s2 = Section(2, "MW 10:00 AM - 11:30 AM", "25/30", "OK")
        self.assertTrue(s1.is_full())
        self.assertFalse(s2.is_full())

    def test_is_at_risk(self):
        s1 = Section(1, "MW 10:00 AM - 11:30 AM", "0/30", "AT-RISK")
        s2 = Section(2, "MW 10:00 AM - 11:30 AM", "5/30", "AT-RISK") # total >= 20 and current < 6
        s3 = Section(3, "MW 10:00 AM - 11:30 AM", "15/30", "OK")
        self.assertTrue(s1.is_at_risk())
        self.assertTrue(s2.is_at_risk())
        self.assertFalse(s3.is_at_risk())

class TestConflictDetector(unittest.TestCase):
    def test_has_conflict_overlapping(self):
        s1 = Section(1, "MW 10:00 AM - 11:30 AM", "15/30", "OK")
        s2 = Section(2, "MW 11:00 AM - 12:30 PM", "15/30", "OK")
        self.assertTrue(ConflictDetector.has_conflict(s1, s2))

    def test_has_conflict_non_overlapping_time(self):
        s1 = Section(1, "MW 10:00 AM - 11:30 AM", "15/30", "OK")
        s2 = Section(2, "MW 12:00 PM - 01:30 PM", "15/30", "OK")
        self.assertFalse(ConflictDetector.has_conflict(s1, s2))

    def test_has_conflict_non_overlapping_days(self):
        s1 = Section(1, "MW 10:00 AM - 11:30 AM", "15/30", "OK")
        s2 = Section(2, "TTh 10:00 AM - 11:30 AM", "15/30", "OK")
        self.assertFalse(ConflictDetector.has_conflict(s1, s2))

if __name__ == '__main__':
    unittest.main()
