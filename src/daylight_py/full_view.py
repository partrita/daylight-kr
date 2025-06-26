import datetime
from .calculations import SunTimes
from rich.console import Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress_bar import ProgressBar
from rich.align import Align
from rich.rule import Rule

# TERMINAL_WIDTH can be dynamic with Rich, but we might use it for some fixed calculations if needed.
# However, Rich components often handle width automatically or via their own width parameters.

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

def render_progress_bar(day_length_seconds, total_seconds_in_day=24*60*60, bar_width=60):
    """Renders a simple text progress bar for daylight."""
    if day_length_seconds is None or day_length_seconds < 0:
        return "." * bar_width

    filled_proportion = day_length_seconds / total_seconds_in_day
    filled_length = int(filled_proportion * bar_width)

    # Simplified representation: R for rise, S for set, - for light, . for dark
    # This is a very rough approximation and doesn't show actual sun position.
    if filled_length == 0: # Polar night
        return "." * bar_width
    if filled_length >= bar_width: # Polar day
        return "R" + ("-" * (bar_width - 2)) + "S" if bar_width > 1 else "-" * bar_width

    bar = "R"
    bar += "-" * (filled_length - 2 if filled_length > 1 else 0)
    bar += "S"
    bar += "." * (bar_width - filled_length -1) # -1 for the S
    # This function is not directly used by Rich progress bar but can be kept for reference
    # or if a custom text-based bar is still desired somewhere.
    # Rich's ProgressBar will handle its own rendering.
    return bar[:bar_width]


def create_full_output(
    query_date: datetime.date,
    sun_times_today: SunTimes,
    sun_times_yesterday: SunTimes,
    ten_day_projection: list, # List of (date, SunTimes) tuples
    ip_info: dict = None, # {'ip': '...', 'latitude': ..., 'longitude': ...}
    offline_mode: bool = False
) -> Group:
    """
    Generates a Rich Group object containing the full daylight information,
    formatted with Rich components like Panel, Table, ProgressBar.
    """
    renderables = []

    # Header
    if offline_mode:
        renderables.append(Align.center(Text("Offline Mode", style="bold yellow")))

    renderables.append(Align.center(Text(f"Today's daylight ({query_date.strftime('%Y-%m-%d')})", style="bold cyan")))
    renderables.append(Rule(style="cyan"))

    # Today's sun times
    today_times_text = Text(justify="center")
    if sun_times_today.polar_day:
        today_times_text.append("POLAR DAY\n(Sun is up all day)", style="bold yellow")
    elif sun_times_today.polar_night:
        today_times_text.append("POLAR NIGHT\n(Sun is down all day)", style="bold blue")
    else:
        rises_str = format_time_optional_hm(sun_times_today.rises)
        noon_str = format_time_optional_hm(sun_times_today.noon)
        sets_str = format_time_optional_hm(sun_times_today.sets)
        today_times_text.append(Text.assemble(
            ("Rises: ", "bold"), (rises_str, "green"), "  ",
            ("Noon: ", "bold"), (noon_str, "yellow"), "  ",
            ("Sets: ", "bold"), (sets_str, "magenta")
        ))
    renderables.append(Align.center(today_times_text))
    renderables.append("") # Spacer

    # Day length panel
    length_today_str = format_timedelta_hm(sun_times_today.length)
    change_val = sun_times_today.length - sun_times_yesterday.length if sun_times_today.length is not None and sun_times_yesterday.length is not None else None
    change_str = format_timedelta_change(change_val)

    change_style = "green" if change_val and change_val.total_seconds() >= 0 else "red" if change_val else ""

    day_length_content = Text.assemble(
        ("Daylight for: ", "bold"), (length_today_str, "bold orange1"), "\n",
        ("Versus yesterday: ", "bold"), (change_str, f"bold {change_style}")
    )
    renderables.append(Panel(Align.center(day_length_content), title="[b]Day Length[/b]", border_style="green", expand=False))
    renderables.append("")


    # Progress bar for daylight
    # Total seconds in a day for progress bar calculation
    total_seconds_in_day = 24 * 60 * 60
    day_seconds = 0
    bar_title = "Daylight Progress"

    if sun_times_today.polar_day:
        day_seconds = total_seconds_in_day
        bar_title = "Polar Day (24h Daylight)"
    elif sun_times_today.polar_night:
        day_seconds = 0
        bar_title = "Polar Night (0h Daylight)"
    elif sun_times_today.length is not None:
        day_seconds = sun_times_today.length.total_seconds()

    # Ensure day_seconds is not negative if length is None for some reason
    day_seconds = max(0, day_seconds)

    progress_bar = ProgressBar(total=total_seconds_in_day, completed=day_seconds, width=50) # Rich will manage width better
    renderables.append(Align.center(Group(Text(bar_title, justify="center"), progress_bar)))
    renderables.append("")


    # Ten day projection table
    projection_table = Table(title="[b]Ten Day Projection[/b]", show_header=True, header_style="bold magenta", border_style="blue")
    projection_table.add_column("Date", style="dim", width=12, justify="center")
    projection_table.add_column("Sunrise", justify="center")
    projection_table.add_column("Sunset", justify="center")
    projection_table.add_column("Length", justify="center", style="green")

    for proj_date, proj_st in ten_day_projection:
        date_str = proj_date.strftime("%a %b %d")
        if proj_st.polar_day:
            rise_str, set_str, len_str = "[yellow]POLAR[/]", "[yellow]DAY[/]", format_timedelta_hm(proj_st.length)
        elif proj_st.polar_night:
            rise_str, set_str, len_str = "[blue]POLAR[/]", "[blue]NIGHT[/]", format_timedelta_hm(proj_st.length)
        else:
            rise_str = format_time_optional_hm(proj_st.rises)
            set_str = format_time_optional_hm(proj_st.sets)
            len_str = format_timedelta_hm(proj_st.length)
        projection_table.add_row(date_str, rise_str, set_str, len_str)
    renderables.append(Align.center(projection_table))
    renderables.append("")

    # Your stats panel
    if ip_info:
        stats_content = Text()
        lat = ip_info.get('latitude')
        lon = ip_info.get('longitude')
        tz = ip_info.get('timezone') # This might be a pytz object or string

        loc_str = f"Lat {lat:.2f}, Lon {lon:.2f}" if lat is not None and lon is not None else "N/A"
        stats_content.append(Text.assemble(("Location: ", "bold"), loc_str, "\n"))
        stats_content.append(Text.assemble(("IP Address: ", "bold"), ip_info.get('ip', 'N/A'), "\n"))

        tz_name = str(tz.zone) if hasattr(tz, 'zone') else str(tz) if tz else "N/A" # Handle both pytz object and string
        stats_content.append(Text.assemble(("Timezone: ", "bold"), tz_name))

        renderables.append(Panel(Align.center(stats_content), title="[b]Your Stats[/b]", border_style="yellow", expand=False))

    return Group(*renderables)


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

    mock_ip_info_london = { # Renamed to avoid conflict
        "ip": "8.8.8.8",
        "latitude": 51.51,
        "longitude": -0.13,
        "timezone": tz_london # Pass the pytz object directly
    }

    console.print("--- Full Output (London) ---")
    full_output_london = create_full_output(
        query_date=today,
        sun_times_today=st_today,
        sun_times_yesterday=st_yesterday,
        ten_day_projection=projection_data,
        ip_info=mock_ip_info_london, # Use renamed variable
        offline_mode=False
    )
    console.print(full_output_london)

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
        "timezone": tz_tromso # Pass the pytz object
    }
    console.print("\n--- Full Output (Tromsø Winter - Polar Night) ---")
    full_output_tromso_winter = create_full_output(
        query_date=winter_date,
        sun_times_today=st_today_tromso_winter,
        sun_times_yesterday=st_yesterday_tromso_winter,
        ten_day_projection=projection_tromso_winter,
        ip_info=mock_ip_info_tromso,
        offline_mode=True
    )
    console.print(full_output_tromso_winter)
