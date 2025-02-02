import re
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import json
import sys


def save_to_json(data, filename):
    try:
        with open(filename, "w") as file:
            json.dump(data, file, indent=4)
    except TypeError:
        print("Error writing data to json file. Exiting...")
        sys.exit(1)


def split_numbers_and_letters(input_string):
    match = re.match(r"(\d+)([a-zA-Z]+)$", input_string)
    if match:
        return int(match.group(1)), match.group(
            2
        )  # Return numbers and letters separately
    return None, None  # Return None if the pattern doesn't match


def get_time_unit(unit):
    if unit == "d":
        return "day"
    elif unit == "h":
        return "hour"
    elif unit == "m":
        return "minute"


def convert_input_to_days_hours_minutes(tf, numCandles):
    value, unit = split_numbers_and_letters(tf)
    total_num_units = value * numCandles
    # Convert the input based on the unit (days, hours, or minutes)
    if unit == "d":
        total_minutes = total_num_units * 24 * 60
    elif unit == "h":
        total_minutes = total_num_units * 60
    elif unit == "m":
        total_minutes = total_num_units
    else:
        raise ValueError("Invalid unit. Please provide 'days', 'hours', or 'minutes'.")

    # Convert total minutes into days, hours, and minutes
    total_days = total_minutes // (24 * 60)
    remaining_minutes = total_minutes % (24 * 60)
    total_hours = remaining_minutes // 60
    total_minutes = remaining_minutes % 60

    return total_days, total_hours, total_minutes


def get_datetimes(candleData):
    for candle in candleData:
        # Convert to datetime in UTC
        utc_time = datetime.fromtimestamp(candle["t"], tz=timezone.utc)

        # Convert to Adelaide time
        adelaide_time = utc_time.astimezone(ZoneInfo("Australia/Adelaide"))
        candle["day"] = adelaide_time.strftime("%a")
        candle["datetime"] = adelaide_time.strftime("%Y-%m-%d %H:%M:%S")
