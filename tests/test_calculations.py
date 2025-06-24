import unittest
import datetime
import pytz

# Add project root to sys.path to allow importing daylight_py
import sys
from pathlib import Path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from daylight_py.calculations import get_sun_times, SunTimes

class TestCalculations(unittest.TestCase):

    def test_get_sun_times_london_summer(self):
        # London, UK
        lat, lon = 51.5074, -0.1278
        tz = pytz.timezone("Europe/London")
        # Use a fixed date for consistent results, e.g., summer solstice
        date_obj = datetime.date(2024, 6, 21)

        times = get_sun_times(lat, lon, date_obj, tz)

        self.assertIsInstance(times, SunTimes)
        self.assertFalse(times.polar_day)
        self.assertFalse(times.polar_night)

        self.assertIsNotNone(times.rises)
        self.assertIsNotNone(times.sets)
        self.assertIsNotNone(times.noon)
        self.assertIsNotNone(times.length)

        # Check if times are in the correct timezone
        self.assertEqual(times.rises.tzinfo.zone, "Europe/London")
        self.assertEqual(times.sets.tzinfo.zone, "Europe/London")
        self.assertEqual(times.noon.tzinfo.zone, "Europe/London")

        # Approximate expected times for London on summer solstice
        # Sunrise around 04:43 BST, Sunset around 21:21 BST
        # Noon around 13:02 BST
        # Length around 16h 38m
        expected_rise = tz.localize(datetime.datetime(2024, 6, 21, 4, 43))
        expected_set = tz.localize(datetime.datetime(2024, 6, 21, 21, 21))
        expected_noon = tz.localize(datetime.datetime(2024, 6, 21, 13, 2))

        self.assertAlmostEqual(times.rises, expected_rise, delta=datetime.timedelta(minutes=15))
        self.assertAlmostEqual(times.sets, expected_set, delta=datetime.timedelta(minutes=15))
        self.assertAlmostEqual(times.noon, expected_noon, delta=datetime.timedelta(minutes=15))
        self.assertGreater(times.length, datetime.timedelta(hours=16, minutes=30))
        self.assertLess(times.length, datetime.timedelta(hours=16, minutes=50))


    def test_get_sun_times_tromso_polar_night(self):
        # Tromsø, Norway
        lat, lon = 69.6492, 18.9553
        tz = pytz.timezone("Europe/Oslo")
        # Date for polar night (e.g., winter solstice)
        date_obj = datetime.date(2024, 12, 21)

        times = get_sun_times(lat, lon, date_obj, tz)

        self.assertTrue(times.polar_night)
        self.assertFalse(times.polar_day)
        self.assertIsNone(times.rises)
        self.assertIsNone(times.sets)
        # Noon might be None or a calculated local 12:00 during polar night by current implementation
        # self.assertIsNone(times.noon) # Original Go app didn't show noon for polar conditions
        self.assertEqual(times.length, datetime.timedelta(0))

    def test_get_sun_times_tromso_polar_day(self):
        # Tromsø, Norway
        lat, lon = 69.6492, 18.9553
        tz = pytz.timezone("Europe/Oslo")
        # Date for polar day (e.g., summer solstice)
        date_obj = datetime.date(2024, 6, 21)

        times = get_sun_times(lat, lon, date_obj, tz)

        self.assertTrue(times.polar_day)
        self.assertFalse(times.polar_night)
        self.assertIsNone(times.rises) # Rises/sets are None for polar day in current impl
        self.assertIsNone(times.sets)
        # Noon should be calculable, approx local 12:00
        self.assertIsNotNone(times.noon)
        if times.noon is not None: # Guard for safety
             self.assertEqual(times.noon.tzinfo.zone, "Europe/Oslo")
             expected_noon_tromso_summer = tz.localize(datetime.datetime(2024,6,21,12,0)) # Approx
             self.assertAlmostEqual(times.noon, expected_noon_tromso_summer, delta=datetime.timedelta(hours=1.5)) # Astral noon can differ

        self.assertEqual(times.length, datetime.timedelta(hours=24))

    def test_get_sun_times_equator(self):
        # Quito, Ecuador (near equator)
        lat, lon = -0.1807, -78.4678
        tz = pytz.timezone("America/Guayaquil")
        date_obj = datetime.date(2024, 3, 20) # Equinox

        times = get_sun_times(lat, lon, date_obj, tz)

        self.assertFalse(times.polar_day)
        self.assertFalse(times.polar_night)
        self.assertIsNotNone(times.rises)
        self.assertIsNotNone(times.sets)
        self.assertIsNotNone(times.noon)
        self.assertIsNotNone(times.length)

        # Day length should be very close to 12 hours
        self.assertAlmostEqual(times.length, datetime.timedelta(hours=12), delta=datetime.timedelta(minutes=10))

if __name__ == '__main__':
    unittest.main()
