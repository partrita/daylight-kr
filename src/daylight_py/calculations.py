import datetime
from astral import LocationInfo
from astral.sun import sun, SunDirection # SunIsNotVisibleError is not directly exposed in v3 as such for sun()
import pytz

class SunTimes:
    def __init__(self, rises, sets, noon, length, polar_night=False, polar_day=False, timezone=pytz.utc):
        self.rises = rises
        self.sets = sets
        self.noon = noon
        # Ensure length is always a timedelta, defaulting to zero if None is passed.
        if length is None:
            self.length = datetime.timedelta(0)
        elif not isinstance(length, datetime.timedelta):
            # Fallback if a non-timedelta type is somehow passed (though unlikely from get_sun_times)
            self.length = datetime.timedelta(0)
            # Optionally, log a warning here if logging facility was available
            # print(f"Warning: SunTimes received non-timedelta length: {length}", file=sys.stderr)
        else:
            self.length = length
        self.polar_night = polar_night
        self.polar_day = polar_day
        self.timezone = timezone # Store timezone for consistent output

    def __repr__(self):
        return (f"SunTimes(rises={self.rises}, sets={self.sets}, noon={self.noon}, length={self.length}, "
                f"polar_night={self.polar_night}, polar_day={self.polar_day}, timezone={self.timezone})")

def get_sun_times(latitude, longitude, date_obj, timezone_pytz):
    """
    Calculates sunrise, sunset, solar noon, and day length for a given location and date.

    Args:
        latitude (float): Latitude of the location.
        longitude (float): Longitude of the location.
        date_obj (datetime.date): The date for which to calculate sun times.
        timezone_pytz (pytz.timezone): The timezone for the location.

    Returns:
        SunTimes: An object containing sunrise, sunset, noon, day length, and polar day/night status.
                  Times are timezone-aware (UTC by default from astral, then localized).
    """
    city = LocationInfo(timezone=timezone_pytz.zone, latitude=latitude, longitude=longitude)

    # Astral's sun function needs a datetime.date object and observer_elevation for more accuracy,
    # but default (sea level) is fine for this application.
    # It returns times in UTC by default.

    try:
        # In Astral v3, if an event like sunrise/sunset doesn't occur,
        # it raises a ValueError for that specific key access if not present,
        # or the sun() call itself might raise ValueError if no events occur.
        # More robustly, check for individual events.

        s = sun(city.observer, date=date_obj, tzinfo=pytz.utc)

        # It's safer to attempt to get each value and handle potential KeyErrors
        # if sun() itself doesn't raise ValueError for total polar conditions.
        # However, the documentation implies sun() will raise ValueError if events are not found.

        sunrise_utc = s.get("sunrise")
        sunset_utc = s.get("sunset")
        noon_utc = s.get("noon") # Noon should generally be present even in polar day.

        if sunrise_utc is None or sunset_utc is None:
            # This condition suggests a polar day/night scenario for rise/set
            raise ValueError("Sunrise or sunset did not occur.")


        # Localize times to the target timezone
        sunrise_local = sunrise_utc.astimezone(timezone_pytz)
        sunset_local = sunset_utc.astimezone(timezone_pytz)
        noon_local = noon_utc.astimezone(timezone_pytz) if noon_utc else None

        day_length = sunset_utc - sunrise_utc # Duration is the same regardless of TZ

        return SunTimes(
            rises=sunrise_local,
            sets=sunset_local,
            noon=noon_local,
            length=day_length,
            timezone=timezone_pytz
        )
    except ValueError: # Catch ValueError for missing sun events (polar day/night)
        # Determine if it's polar day or polar night
        is_northern_hemisphere = latitude >= 0
        month = date_obj.month

        # Simplified logic similar to the Go version
        # (This is a common heuristic for polar regions)
        is_summer_month = (month > 3 and month < 10) # April to September

        polar_day = False
        polar_night = False

        if is_northern_hemisphere:
            if is_summer_month:
                polar_day = True
            else:
                polar_night = True
        else: # Southern Hemisphere
            if is_summer_month:
                polar_night = True
            else:
                polar_day = True

        length = datetime.timedelta(hours=24) if polar_day else datetime.timedelta(0)

        # For polar day/night, specific rise/set times are not meaningful.
        # We can set them to the beginning/end of the day or None.
        # The Go code used nilTime. Here, None is more Pythonic.
        # Noon is also tricky. For polar day, it's an actual event. For polar night, it's not.

        # Represent "no rise/set" as None
        # For noon, if it's polar day, it's still the sun's highest point.
        # If polar night, noon is not solar noon.
        # The original app didn't show noon for polar night/day in the main display.
        # Let's set rise/set to None, and noon to a calculated local noon if polar day.

        calculated_noon_local = None
        if polar_day:
            # For polar day, sun is always up. Noon is still relevant.
            # We can approximate it or get it if astral provides it even during polar day.
            # If `sun()` errored, `s` is not defined.
            # We'll use the local midday time as a stand-in for "noon" during polar day.
            calculated_noon_local = timezone_pytz.localize(datetime.datetime.combine(date_obj, datetime.time(12,0,0)))


        return SunTimes(
            rises=None,
            sets=None,
            noon=calculated_noon_local, # Or None if preferred for consistency when rise/set is None
            length=length,
            polar_day=polar_day,
            polar_night=polar_night,
            timezone=timezone_pytz
        )

if __name__ == '__main__':
    # Example Usage (London)
    try:
        # London
        tz_london_str = "Europe/London"
        tz_london = pytz.timezone(tz_london_str)
        today_london = datetime.datetime.now(tz_london).date()

        print(f"\n--- London ({today_london}, {tz_london_str}) ---")
        london_times = get_sun_times(51.5074, 0.1278, today_london, tz_london)
        if london_times.polar_day:
            print("Polar Day (Sun always up)")
        elif london_times.polar_night:
            print("Polar Night (Sun always down)")
        else:
            print(f"  Sunrise: {london_times.rises.strftime('%H:%M:%S %Z') if london_times.rises else 'N/A'}")
            print(f"  Sunset:  {london_times.sets.strftime('%H:%M:%S %Z') if london_times.sets else 'N/A'}")
            print(f"  Noon:    {london_times.noon.strftime('%H:%M:%S %Z') if london_times.noon else 'N/A'}")
        print(f"  Length:  {str(london_times.length)}")

        # Example Usage (Tromsø, Norway - potential for polar night/day)
        tz_tromso_str = "Europe/Oslo"
        tz_tromso = pytz.timezone(tz_tromso_str)

        print(f"\n--- Tromsø (Summer, {tz_tromso_str}) ---")
        summer_date_tromso = datetime.date(2024, 6, 21)
        tromso_summer_times = get_sun_times(69.6492, 18.9553, summer_date_tromso, tz_tromso)
        if tromso_summer_times.polar_day:
            print("Polar Day (Sun always up)")
        elif tromso_summer_times.polar_night:
            print("Polar Night (Sun always down)")
        else:
            print(f"  Sunrise: {tromso_summer_times.rises.strftime('%H:%M:%S %Z') if tromso_summer_times.rises else 'N/A'}")
            print(f"  Sunset:  {tromso_summer_times.sets.strftime('%H:%M:%S %Z') if tromso_summer_times.sets else 'N/A'}")
            print(f"  Noon:    {tromso_summer_times.noon.strftime('%H:%M:%S %Z') if tromso_summer_times.noon else 'N/A'}")
        print(f"  Length:  {str(tromso_summer_times.length)}")

        print(f"\n--- Tromsø (Winter, {tz_tromso_str}) ---")
        winter_date_tromso = datetime.date(2024, 12, 21)
        tromso_winter_times = get_sun_times(69.6492, 18.9553, winter_date_tromso, tz_tromso)
        if tromso_winter_times.polar_day:
            print("Polar Day (Sun always up)")
        elif tromso_winter_times.polar_night:
            print("Polar Night (Sun always down)")
        else:
            print(f"  Sunrise: {tromso_winter_times.rises.strftime('%H:%M:%S %Z') if tromso_winter_times.rises else 'N/A'}")
            print(f"  Sunset:  {tromso_winter_times.sets.strftime('%H:%M:%S %Z') if tromso_winter_times.sets else 'N/A'}")
            print(f"  Noon:    {tromso_winter_times.noon.strftime('%H:%M:%S %Z') if tromso_winter_times.noon else 'N/A'}")
        print(f"  Length:  {str(tromso_winter_times.length)}")

    except Exception as e:
        print(f"An error occurred: {e}")
