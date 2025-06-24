# Daylight Python Version

This is a Python port of the Go command-line program `daylight` (originally by jbreckmckye).
It displays sunrise, sunset, solar noon times, day length, and projects these changes over the next ten days.

The tool uses your IP-based location (via ipinfo.io) by default, or you can specify location and timezone manually.

## Features

*   Calculates sunrise, sunset, solar noon, and day length.
*   Handles normal, polar day, and polar night conditions.
*   Fetches location data based on your IP address (requires internet).
*   Allows manual override of latitude, longitude, and timezone for offline use or specific locations.
*   Provides output in three formats:
    *   Full, detailed human-readable text (default).
    *   Short, condensed summary (`--short`).
    *   JSON output for machine readability (`--json`).
*   Shows a 10-day projection of daylight changes (in full view).

## Requirements

*   Python 3.7+
*   Libraries: `requests`, `pytz`, `astral` (see `requirements.txt`)

## Usage

1.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
    Or, if setting up for development including test dependencies (e.g. using `setup.cfg`):
    ```bash
    pip install .[test]
    ```
    (Assuming `pyproject.toml` and `setup.cfg` are configured for this)


2.  **Run the script (after installation or directly):**
    If installed (e.g., `pip install .`):
    ```bash
    daylight-py [OPTIONS]
    ```
    (This assumes an entry point `daylight-py` is defined in `setup.cfg`)

    Or run directly:
    ```bash
    python main.py [OPTIONS]
    ```

    **Examples:**

    *   Get today's data for your IP location:
        ```bash
        python main.py
        ```

    *   Override location and timezone (offline operation possible if all three are given):
        ```bash
        python main.py --latitude="-33.92" --longitude="18.42" --timezone="Africa/Johannesburg"
        ```

    *   Short summary:
        ```bash
        python main.py --short
        ```

    *   JSON output:
        ```bash
        python main.py --json
        ```

    *   Data for another date:
        ```bash
        python main.py --date="2025-12-31"
        ```

    *   Show help:
        ```bash
        python main.py --help
        ```

## Development

*   **Running tests:**
    ```bash
    python -m unittest discover -s tests
    ```
    Or if `pytest` is added as a test runner:
    ```bash
    pytest
    ```

## Original Go Project

For the original Go version and more context, please visit:
[https://github.com/jbreckmckye/daylight](https://github.com/jbreckmckye/daylight)

## License

This Python port is provided under the same license as the original project (GPL).
The original `LICENSE` file from the Go project is included in this repository.
Please refer to it for full licensing details.
