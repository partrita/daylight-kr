import unittest
import datetime
import pytz

# Add project root to sys.path to allow importing daylight_py
import sys
from pathlib import Path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from daylight_py.calculations import SunTimes, get_sun_times
from daylight_py.json_view import create_json_output
from daylight_py.condensed_view import create_condensed_output
from daylight_py.full_view import create_full_output

class TestViews(unittest.TestCase):

    def setUp(self):
        # Common data for tests
        self.lat_london, self.lon_london = 51.5074, -0.1278
        self.tz_london = pytz.timezone("Europe/London")
        self.test_date = datetime.date(2024, 7, 15) # A normal day
        self.yesterday_date = self.test_date - datetime.timedelta(days=1)

        self.sun_times_today = get_sun_times(self.lat_london, self.lon_london, self.test_date, self.tz_london)
        self.sun_times_yesterday = get_sun_times(self.lat_london, self.lon_london, self.yesterday_date, self.tz_london)

        # For polar conditions
        self.lat_tromso, self.lon_tromso = 69.6492, 18.9553
        self.tz_tromso = pytz.timezone("Europe/Oslo")
        self.polar_night_date = datetime.date(2024, 12, 21)
        self.polar_day_date = datetime.date(2024, 6, 21)

        self.st_polar_night = get_sun_times(self.lat_tromso, self.lon_tromso, self.polar_night_date, self.tz_tromso)
        self.st_polar_night_yesterday = get_sun_times(self.lat_tromso, self.lon_tromso, self.polar_night_date - datetime.timedelta(days=1), self.tz_tromso)

        self.st_polar_day = get_sun_times(self.lat_tromso, self.lon_tromso, self.polar_day_date, self.tz_tromso)
        self.st_polar_day_yesterday = get_sun_times(self.lat_tromso, self.lon_tromso, self.polar_day_date - datetime.timedelta(days=1), self.tz_tromso)


    def test_json_output_normal_day(self):
        json_str = create_json_output(
            query_date=self.test_date,
            sun_times_today=self.sun_times_today,
            sun_times_yesterday=self.sun_times_yesterday,
            ip_address="1.2.3.4",
            location={"latitude": self.lat_london, "longitude": self.lon_london}
        )
        self.assertTrue(json_str.startswith("{"))
        self.assertIn("\"rises\":", json_str)
        self.assertIn("\"ip_address\": \"1.2.3.4\"", json_str)
        import json # Check it's valid JSON
        json.loads(json_str)


    def test_json_output_polar_night(self):
        json_str = create_json_output(
            query_date=self.polar_night_date,
            sun_times_today=self.st_polar_night,
            sun_times_yesterday=self.st_polar_night_yesterday
        )
        self.assertIn("\"polar_night\": true", json_str)
        self.assertIn("\"rises\": null", json_str) # Expect null if no rise/set
        import json
        json.loads(json_str)

    def test_condensed_output_normal_day(self):
        condensed_str = create_condensed_output(self.sun_times_today, self.sun_times_yesterday)
        self.assertIn("Rises:", condensed_str)
        self.assertIn("Sets:", condensed_str)
        self.assertIn("Length:", condensed_str)
        self.assertIn("Change:", condensed_str)

    def test_condensed_output_polar_day(self):
        condensed_str = create_condensed_output(self.st_polar_day, self.st_polar_day_yesterday)
        self.assertIn("Polar Day", condensed_str)
        self.assertNotIn("Rises:", condensed_str)
        self.assertIn("Length: 24 hrs, 0 mins", condensed_str)


    def test_full_output_normal_day(self):
        ten_day_proj = []
        for i in range(1, 3): # Shorter projection for test speed
            proj_d = self.test_date + datetime.timedelta(days=i)
            proj_st = get_sun_times(self.lat_london, self.lon_london, proj_d, self.tz_london)
            ten_day_proj.append((proj_d, proj_st))

        ip_info = {"ip": "1.2.3.4", "latitude": self.lat_london, "longitude": self.lon_london}

        full_str = create_full_output(
            query_date=self.test_date,
            sun_times_today=self.sun_times_today,
            sun_times_yesterday=self.sun_times_yesterday,
            ten_day_projection=ten_day_proj,
            ip_info=ip_info
        )
        self.assertIn("Today's daylight", full_str)
        self.assertIn("Ten day projection", full_str)
        self.assertIn("Your stats", full_str)
        self.assertIn(ip_info["ip"], full_str)

    def test_full_output_polar_night(self):
        ten_day_proj = [] # Keep it simple for this test
        ip_info = {"latitude": self.lat_tromso, "longitude": self.lon_tromso} # No IP for offline feel

        full_str = create_full_output(
            query_date=self.polar_night_date,
            sun_times_today=self.st_polar_night,
            sun_times_yesterday=self.st_polar_night_yesterday,
            ten_day_projection=ten_day_proj,
            ip_info=ip_info,
            offline_mode=True
        )
        self.assertIn("POLAR NIGHT", full_str)
        self.assertIn("Offline Mode", full_str)
        self.assertIn(f"{self.lat_tromso:.2f}", full_str)


if __name__ == '__main__':
    unittest.main()
