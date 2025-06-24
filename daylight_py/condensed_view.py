import datetime
from .calculations import SunTimes # Assuming SunTimes is in calculations.py

def format_time_optional_hm(dt_obj):
    """Formats a datetime object to HH:MM, or returns 'N/A' if dt_obj is None."""
    if dt_obj:
        return dt_obj.strftime("%H:%M")
    return "N/A"

def format_timedelta_to_hm_str(delta):
    """Formats a timedelta object to 'X hrs, Y mins' string, or 'N/A' if delta is None."""
    if delta is None:
        return "N/A"

    total_seconds = int(delta.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    return f"{hours} hrs, {minutes} mins"

def create_condensed_output(sun_times_today: SunTimes, sun_times_yesterday: SunTimes):
    """
    Generates a condensed string summary of daylight information.
    """
    lines = []

    if sun_times_today.polar_day:
        lines.append("Polar Day")
        lines.append(f"Length: {format_timedelta_to_hm_str(sun_times_today.length)}")
    elif sun_times_today.polar_night:
        lines.append("Polar Night")
        lines.append(f"Length: {format_timedelta_to_hm_str(sun_times_today.length)}")
    else:
        lines.append(f"Rises:  {format_time_optional_hm(sun_times_today.rises)}")
        lines.append(f"Sets:   {format_time_optional_hm(sun_times_today.sets)}")
        lines.append(f"Length: {format_timedelta_to_hm_str(sun_times_today.length)}")

    # Calculate change in day length
    if sun_times_today.length is not None and sun_times_yesterday.length is not None:
        change_in_length = sun_times_today.length - sun_times_yesterday.length
        total_seconds = int(change_in_length.total_seconds())
        sign = "+" if total_seconds >= 0 else "-"
        total_seconds = abs(total_seconds)
        minutes = total_seconds // 60
        seconds = total_seconds % 60 # Original Go app shows minutes and seconds for change
        lines.append(f"Change: {sign}{minutes}m {seconds}s")
    else:
        lines.append("Change: N/A")

    return "\n".join(lines)

if __name__ == '__main__':
    # Example Usage
    import pytz
    from .calculations import get_sun_times # Make sure this import works based on your structure

    # London example
    tz_london_str = "Europe/London"
    tz_london = pytz.timezone(tz_london_str)
    today_date = datetime.datetime.now(tz_london).date()
    yesterday_date = today_date - datetime.timedelta(days=1)

    st_today_london = get_sun_times(51.5074, 0.1278, today_date, tz_london)
    st_yesterday_london = get_sun_times(51.5074, 0.1278, yesterday_date, tz_london)

    print("--- Condensed Output (London) ---")
    print(create_condensed_output(st_today_london, st_yesterday_london))

    # Tromsø example (Polar Night in December)
    tz_tromso_str = "Europe/Oslo"
    tz_tromso = pytz.timezone(tz_tromso_str)
    dec_21 = datetime.date(2024, 12, 21)
    dec_20 = dec_21 - datetime.timedelta(days=1)

    st_today_tromso_winter = get_sun_times(69.6492, 18.9553, dec_21, tz_tromso)
    st_yesterday_tromso_winter = get_sun_times(69.6492, 18.9553, dec_20, tz_tromso)

    print("\n--- Condensed Output (Tromsø Winter - Polar Night) ---")
    print(create_condensed_output(st_today_tromso_winter, st_yesterday_tromso_winter))

    # Tromsø example (Polar Day in June)
    jun_21 = datetime.date(2024, 6, 21)
    jun_20 = jun_21 - datetime.timedelta(days=1)
    st_today_tromso_summer = get_sun_times(69.6492, 18.9553, jun_21, tz_tromso)
    st_yesterday_tromso_summer = get_sun_times(69.6492, 18.9553, jun_20, tz_tromso)

    print("\n--- Condensed Output (Tromsø Summer - Polar Day) ---")
    print(create_condensed_output(st_today_tromso_summer, st_yesterday_tromso_summer))
