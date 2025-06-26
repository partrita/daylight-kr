import datetime
from .calculations import SunTimes # Assuming SunTimes is in calculations.py

# Width for formatting, can be adjusted
TERMINAL_WIDTH = 80

def format_time_optional_hm(dt_obj, default_val="--:--"):
    """Formats a datetime object to HH:MM, or returns default_val if dt_obj is None."""
    if dt_obj:
        return dt_obj.strftime("%H:%M")
    return default_val

def format_timedelta_hm(delta, default_val="N/A"):
    """Formats a timedelta to 'X hrs, Y mins' or 'Y mins' if hours is 0, or default_val."""
    if delta is None:
        return default_val

    total_seconds = int(delta.total_seconds())
    if total_seconds < 0: # Should not happen for day length, but good practice
        return default_val

    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60

    if hours > 0:
        return f"{hours} hrs, {minutes} mins"
    else:
        return f"{minutes} mins"

def format_timedelta_change(delta, default_val="N/A"):
    """Formats a timedelta to '+Xm Ys' or '-Xm Ys'."""
    if delta is None:
        return default_val

    total_seconds = int(delta.total_seconds())
    sign = "+" if total_seconds >= 0 else "-"
    total_seconds = abs(total_seconds)

    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{sign}{minutes}m {seconds}s"

def render_progress_bar_new(
    current_time_local: datetime.datetime,
    sunrise_local: datetime.datetime | None,
    sunset_local: datetime.datetime | None,
    polar_day: bool,
    polar_night: bool,
    bar_width: int = 60
):
    """Renders a text progress bar indicating current time relative to daylight."""

    minutes_in_day = 24 * 60
    # Handle potential division by zero if bar_width is 0, though unlikely.
    minutes_per_char = minutes_in_day / bar_width if bar_width > 0 else minutes_in_day

    def get_char_pos(dt_obj: datetime.datetime | None) -> int | None:
        if dt_obj is None:
            return None
        time_in_minutes = dt_obj.hour * 60 + dt_obj.minute
        # Ensure pos is an int and within bounds
        pos = int(time_in_minutes / minutes_per_char) if minutes_per_char > 0 else 0
        return min(max(pos, 0), bar_width - 1 if bar_width > 0 else 0)

    current_pos = get_char_pos(current_time_local) if current_time_local else None

    bar_chars = ['.'] * bar_width

    if polar_day:
        bar_chars = ['-'] * bar_width
        if bar_width > 0: bar_chars[0] = 'R'
        if bar_width > 1: bar_chars[bar_width - 1] = 'S'
    elif polar_night:
        pass # Already all '.'
    elif sunrise_local and sunset_local:
        sunrise_pos = get_char_pos(sunrise_local)
        sunset_pos = get_char_pos(sunset_local)

        if sunrise_pos is not None and sunset_pos is not None:
            # Fill daylight part
            # This logic assumes sunrise_pos <= sunset_pos for a typical day.
            # More complex scenarios (e.g. sun sets before it rises on a given date due to polar effects)
            # are simplified here. Astral provides events for the given date.
            start_char = min(sunrise_pos, sunset_pos)
            end_char = max(sunrise_pos, sunset_pos)

            # If sunrise is after sunset (e.g. for southern hemisphere summer, date chosen is winter for north)
            # this means it's mostly dark, or light spans across midnight.
            # For this bar, we simplify: if sun rises and sets on this date, show that span as light.
            if sunrise_local < sunset_local: # Normal case: sun rises then sets
                 for i in range(sunrise_pos, sunset_pos + 1):
                    if 0 <= i < bar_width:
                        bar_chars[i] = '-'
            else: # Sun sets then rises (e.g. daylight spans midnight)
                for i in range(0, sunset_pos + 1): # From start of day to sunset
                    if 0 <= i < bar_width: bar_chars[i] = '-'
                for i in range(sunrise_pos, bar_width): # From sunrise to end of day
                     if 0 <= i < bar_width: bar_chars[i] = '-'

            # Place R and S
            if 0 <= sunrise_pos < bar_width: bar_chars[sunrise_pos] = 'R'
            if 0 <= sunset_pos < bar_width: bar_chars[sunset_pos] = 'S'
            # If R and S are at the same spot, S takes precedence if it's different from R.
            # This case is rare (extremely short day/night).
            if sunrise_pos == sunset_pos and 0 <= sunrise_pos < bar_width:
                 bar_chars[sunrise_pos] = '*' # Indicate both rise and set at same char

    # Place 'C' for current time, potentially overwriting R/S if at the same char position
    if current_pos is not None and 0 <= current_pos < bar_width:
        bar_chars[current_pos] = 'C'

    if not bar_chars: return "?" * bar_width # Should not happen if bar_width > 0
    return "".join(bar_chars)


def create_full_output(
    query_date: datetime.date,
    sun_times_today: SunTimes,
    sun_times_yesterday: SunTimes,
    ten_day_projection: list, # List of (date, SunTimes) tuples
    ip_info: dict = None, # {'ip': '...', 'latitude': ..., 'longitude': ...}
    offline_mode: bool = False,
    current_time_utc: datetime.datetime | None = None # Added parameter
):
    """
    Generates the full text output for daylight information.
    """
    lines = []
    separator = "═" * TERMINAL_WIDTH

    # Header
    if offline_mode:
        lines.append("Offline Mode".center(TERMINAL_WIDTH))
    lines.append("Today's daylight".center(TERMINAL_WIDTH))
    lines.append(separator)
    lines.append("") # Spacer

    # Today's sun times
    if sun_times_today.polar_day:
        lines.append("POLAR DAY (Sun is up all day)".center(TERMINAL_WIDTH))
    elif sun_times_today.polar_night:
        lines.append("POLAR NIGHT (Sun is down all day)".center(TERMINAL_WIDTH))
    else:
        rises_str = format_time_optional_hm(sun_times_today.rises)
        noon_str = format_time_optional_hm(sun_times_today.noon)
        sets_str = format_time_optional_hm(sun_times_today.sets)

        # Try to somewhat align these: Rises, Noon, Sets
        # Max label length is "Rises: " = 7. Max time length is "00:00" = 5
        # Field width could be dynamic, or fixed. Let's try semi-fixed for now.
        # Total width: 80. Space for 3 items + labels.
        # Approx 26 chars per item block.
        # Label (7) + Time (5) = 12. Remaining 14 for spacing.
        # "Rises: HH:MM Noon: HH:MM Sets: HH:MM"

        line = f"{'Rises:':<10}{rises_str:<6}"
        line += f"{'Noon:':^20}{noon_str:^6}" # Centered noon
        line += f"{'Sets:':>16}{sets_str:>6}" # Right aligned sets
        # This alignment is tricky without knowing exact spacing of original.
        # A simpler approach:
        line1_today = f"Rises: {rises_str}".ljust(TERMINAL_WIDTH // 3) + \
                      f"Noon: {noon_str}".center(TERMINAL_WIDTH // 3) + \
                      f"Sets: {sets_str}".rjust(TERMINAL_WIDTH // 3)
        lines.append(line1_today.center(TERMINAL_WIDTH).rstrip())


    lines.append("") # Spacer

    # Day length
    lines.append("Day length".center(TERMINAL_WIDTH))
    lines.append(separator)
    lines.append("")

    length_today_str = format_timedelta_hm(sun_times_today.length)
    change_str = format_timedelta_change(sun_times_today.length - sun_times_yesterday.length if sun_times_today.length is not None and sun_times_yesterday.length is not None else None)

    line_len1 = f"Daylight for: {length_today_str}"
    line_len2 = f"versus yesterday: {change_str}"

    # Simple two-column layout
    # Max length of "Daylight for: XX hrs, YY mins" vs "versus yesterday: +XXm YYs"
    # Let's give half width to each roughly
    half_width = TERMINAL_WIDTH // 2
    lines.append(f"{line_len1:<{half_width}}{line_len2:>{TERMINAL_WIDTH - half_width}}")
    lines.append("")

    # Progress bar
    progress_bar_width = 60 # Match example
    bar_str = ""
    if current_time_utc and sun_times_today.timezone:
        current_time_local = current_time_utc.astimezone(sun_times_today.timezone)

        # The progress bar should reflect the timeline of the query_date,
        # but the 'C' marker should be based on the current time's time of day.
        # So, we set current_time_local's date part to query_date for positioning 'C'
        # correctly on the historical/future bar.
        # However, the spirit of "current time" is NOW, so we use actual current_time_local.
        # The bar represents the day specified by query_date.
        # 'C' shows where "now" is on such a day's timeline.

        bar_str = render_progress_bar_new(
            current_time_local=current_time_local, # Actual current time, localized
            sunrise_local=sun_times_today.rises,    # This is for query_date
            sunset_local=sun_times_today.sets,      # This is for query_date
            polar_day=sun_times_today.polar_day,
            polar_night=sun_times_today.polar_night,
            bar_width=progress_bar_width
        )
    else:
        # Fallback or if current_time_utc is not provided (should not happen with app.py changes)
        # Or if timezone info is missing from sun_times_today (also unlikely)
        if sun_times_today.polar_day:
            bar_str = "R" + ("-" * (progress_bar_width - 2)) + "S" if progress_bar_width > 1 else "-" * progress_bar_width
        elif sun_times_today.polar_night:
            bar_str = "." * progress_bar_width
        else: # Could try to use the old bar if length is available, but ? is safer if C cannot be shown
            bar_str = "?" * progress_bar_width

    lines.append(bar_str.center(TERMINAL_WIDTH))
    lines.append("")

    # Ten day projection
    lines.append("Ten day projection".center(TERMINAL_WIDTH))
    lines.append(separator)
    lines.append("")

    # Table headers
    # DATE (15) | SUNRISE (9) | SUNSET (9) | LENGTH (18)
    # Total: 15 + 9 + 9 + 18 + (3*3 pipes+spaces) = 51 + 9 = 60
    # Let's define column widths
    col_date_w = 16 # "Wed Apr 30"
    col_rise_w = 9  # "05:33"
    col_set_w = 9   # "20:21"
    col_len_w = 20  # "14 hrs, 47 mins"

    header_fmt = f"│ {{:<{col_date_w}}} │ {{:^{col_rise_w}}} │ {{:^{col_set_w}}} │ {{:^{col_len_w}}} │"

    # Calculate the total table width to center it properly
    table_width = col_date_w + col_rise_w + col_set_w + col_len_w + (3 * 3) + 2 # Columns + pipes + spaces + outer borders

    lines.append(header_fmt.format("DATE", "SUNRISE", "SUNSET", "LENGTH").center(TERMINAL_WIDTH)) # Center the whole header

    for proj_date, proj_st in ten_day_projection:
        date_str = proj_date.strftime("%a %b %d") # e.g., Sun Apr 27

        if proj_st.polar_day:
            rise_str, set_str, len_str = "POLAR", "DAY", format_timedelta_hm(proj_st.length)
        elif proj_st.polar_night:
            rise_str, set_str, len_str = "POLAR", "NIGHT", format_timedelta_hm(proj_st.length)
        else:
            rise_str = format_time_optional_hm(proj_st.rises)
            set_str = format_time_optional_hm(proj_st.sets)
            len_str = format_timedelta_hm(proj_st.length)

        lines.append(header_fmt.format(date_str, rise_str, set_str, len_str).center(TERMINAL_WIDTH)) # Center the whole row

    lines.append("")

    # Your stats
    if ip_info:
        lines.append("Your stats".center(TERMINAL_WIDTH))
        lines.append(separator)
        lines.append("")

        loc_str = f"LOCATION  Latitude {ip_info.get('latitude', 'N/A'):.2f}, Longitude {ip_info.get('longitude', 'N/A'):.2f}"
        ip_str = f"IP ADDRESS  {ip_info.get('ip', 'N/A')}"

        # Align these similar to day length section
        lines.append(f"{loc_str:<{TERMINAL_WIDTH // 2 + 5}}{ip_str:>{TERMINAL_WIDTH - (TERMINAL_WIDTH // 2 + 5)}}") # Give a bit more to location
        lines.append("")

    lines.append("") # Final spacer

    return "\n".join(lines)


if __name__ == '__main__':
    # Example Usage
    import pytz
    from .calculations import get_sun_times # Make sure this import works

    tz_london_str = "Europe/London"
    tz_london = pytz.timezone(tz_london_str)
    today = datetime.datetime.now(tz_london).date()
    yesterday = today - datetime.timedelta(days=1)

    st_today = get_sun_times(51.5074, 0.1278, today, tz_london)
    st_yesterday = get_sun_times(51.5074, 0.1278, yesterday, tz_london)

    projection_data = []
    for i in range(1, 11):
        proj_d = today + datetime.timedelta(days=i)
        proj_st = get_sun_times(51.5074, 0.1278, proj_d, tz_london)
        projection_data.append((proj_d, proj_st))

    mock_ip_info = {
        "ip": "8.8.8.8",
        "latitude": 51.51,
        "longitude": -0.13,
        "timezone": tz_london
    }

    print("--- Full Output (London) ---")
    full_output_london = create_full_output(
        query_date=today,
        sun_times_today=st_today,
        sun_times_yesterday=st_yesterday,
        ten_day_projection=projection_data,
        ip_info=mock_ip_info
    )
    print(full_output_london)

    # Example for Polar Night (Tromsø)
    tz_tromso_str = "Europe/Oslo"
    tz_tromso = pytz.timezone(tz_tromso_str)
    winter_date = datetime.date(2024, 12, 21)
    yesterday_winter = winter_date - datetime.timedelta(days=1)

    st_today_tromso_winter = get_sun_times(69.6492, 18.9553, winter_date, tz_tromso)
    st_yesterday_tromso_winter = get_sun_times(69.6492, 18.9553, yesterday_winter, tz_tromso)

    projection_tromso_winter = []
    for i in range(1, 11):
        proj_d = winter_date + datetime.timedelta(days=i)
        proj_st = get_sun_times(69.6492, 18.9553, proj_d, tz_tromso)
        projection_tromso_winter.append((proj_d, proj_st))

    mock_ip_info_tromso = {
        "ip": "9.9.9.9",
        "latitude": 69.65,
        "longitude": 18.96,
        "timezone": tz_tromso
    }
    print("\n--- Full Output (Tromsø Winter - Polar Night) ---")
    full_output_tromso_winter = create_full_output(
        query_date=winter_date,
        sun_times_today=st_today_tromso_winter,
        sun_times_yesterday=st_yesterday_tromso_winter,
        ten_day_projection=projection_tromso_winter,
        ip_info=mock_ip_info_tromso
    )
    print(full_output_tromso_winter)
