import json
import datetime
from .calculations import SunTimes # Assuming SunTimes is in calculations.py

def format_time_optional(dt_obj):
    """Formats a datetime object to HH:MM, or returns None if dt_obj is None."""
    if dt_obj:
        return dt_obj.strftime("%H:%M")
    return None

def format_timedelta_to_hm(delta):
    """Formats a timedelta object to 'X hrs, Y mins' string, or None if delta is None."""
    if delta is None:
        return None

    if isinstance(delta, str): # If it's already a string (e.g. "24 hrs")
        return delta

    total_seconds = int(delta.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    return f"{hours} hrs, {minutes} mins"

def create_json_output(query_date, sun_times_today: SunTimes, sun_times_yesterday: SunTimes, ip_address=None, location=None):
    """
    Generates a JSON string summarizing the daylight information.
    Mirrors the structure of the Go app's JSON output based on README and observed behavior.
    """

    change_in_length_str = None
    if sun_times_today.length is not None and sun_times_yesterday.length is not None:
        change_in_length = sun_times_today.length - sun_times_yesterday.length
        # Format change_in_length with sign
        total_seconds = int(change_in_length.total_seconds())
        sign = "+" if total_seconds >= 0 else "-"
        total_seconds = abs(total_seconds)
        # hours = total_seconds // 3600 # Original Go app only shows minutes and seconds for change
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        change_in_length_str = f"{sign}{minutes}m {seconds}s"


    output_data = {
        "date": query_date.strftime("%Y-%m-%d"),
        "rises": format_time_optional(sun_times_today.rises),
        "sets": format_time_optional(sun_times_today.sets),
        "noon": format_time_optional(sun_times_today.noon),
        "length": format_timedelta_to_hm(sun_times_today.length),
        "length_seconds": int(sun_times_today.length.total_seconds()) if sun_times_today.length is not None else None,
        "change": change_in_length_str,
        "polar_day": sun_times_today.polar_day,
        "polar_night": sun_times_today.polar_night,
    }

    if ip_address:
        output_data["ip_address"] = ip_address
    if location: # location should be a dict with lat, lon
        output_data["latitude"] = location.get("latitude")
        output_data["longitude"] = location.get("longitude")
    if sun_times_today.timezone:
         output_data["timezone"] = str(sun_times_today.timezone)


    return json.dumps(output_data, indent=2)

if __name__ == '__main__':
    # Example Usage
    import pytz
    from .calculations import get_sun_times

    # London example
    tz_london_str = "Europe/London"
    tz_london = pytz.timezone(tz_london_str)
    today = datetime.datetime.now(tz_london).date()
    yesterday = today - datetime.timedelta(days=1)

    # Simulate fetching sun times
    st_today = get_sun_times(51.5074, 0.1278, today, tz_london)
    st_yesterday = get_sun_times(51.5074, 0.1278, yesterday, tz_london)

    json_output = create_json_output(
        query_date=today,
        sun_times_today=st_today,
        sun_times_yesterday=st_yesterday,
        ip_address="123.45.67.89",
        location={"latitude": 51.5074, "longitude": 0.1278}
    )
    print("--- JSON Output (London) ---")
    print(json_output)

    # Tromsø example (Polar Night in December)
    tz_tromso_str = "Europe/Oslo"
    tz_tromso = pytz.timezone(tz_tromso_str)
    dec_21 = datetime.date(2024, 12, 21)
    dec_20 = datetime.date(2024, 12, 20)

    st_today_tromso_winter = get_sun_times(69.6492, 18.9553, dec_21, tz_tromso)
    st_yesterday_tromso_winter = get_sun_times(69.6492, 18.9553, dec_20, tz_tromso)

    json_output_tromso_winter = create_json_output(
        query_date=dec_21,
        sun_times_today=st_today_tromso_winter,
        sun_times_yesterday=st_yesterday_tromso_winter,
        location={"latitude": 69.6492, "longitude": 18.9553}
    )
    print("\n--- JSON Output (Tromsø Winter - Polar Night) ---")
    print(json_output_tromso_winter)

    # Tromsø example (Polar Day in June)
    jun_21 = datetime.date(2024, 6, 21)
    jun_20 = datetime.date(2024, 6, 20)
    st_today_tromso_summer = get_sun_times(69.6492, 18.9553, jun_21, tz_tromso)
    st_yesterday_tromso_summer = get_sun_times(69.6492, 18.9553, jun_20, tz_tromso)

    json_output_tromso_summer = create_json_output(
        query_date=jun_21,
        sun_times_today=st_today_tromso_summer,
        sun_times_yesterday=st_yesterday_tromso_summer,
        location={"latitude": 69.6492, "longitude": 18.9553}
    )
    print("\n--- JSON Output (Tromsø Summer - Polar Day) ---")
    print(json_output_tromso_summer)
