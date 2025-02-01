import requests
import argparse
import re
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import json
import sys

# Example Unix timestamp
timestamp = 1706851200  # Replace with your timestamp


TIME_FRAMES = (
    "1m",
    "2m",
    "3m",
    "4m",
    "5m",
    "10m",
    "15m",
    "20m",
    "30m",
    "45m",
    "1h",
    "2h",
    "3h",
    "4h",
    "8h",
    "12h",
    "1d",
    "1w",
)


def validate_input(args):
    if args.tf not in TIME_FRAMES:
        print("Invalid time frame.")
        exit(1)
    if (
        isinstance(args.numCandles, int)
        and args.numCandles > 0
        and args.numCandles > 1000
    ):
        print("Number of candles must be a positive integer less than 1000")


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


def fetch_bitcoin_history(tf, numCandles, currentPage):
    url = f"https://api.finazon.io/latest/finazon/crypto/time_series?ticker=BTC/USDT&interval={tf}&page={currentPage}&page_size={numCandles}&apikey=27937194b05042048c1ddda8f2fd697dhk"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print("Failed to fetch data")
        return None


def save_to_json(data, filename):
    try:
        with open(filename, "w") as file:
            json.dump(data, file, indent=4)
    except TypeError:
        print("Error writing data to json file. Exiting...")
        sys.exit(1)


def Main():
    parser = argparse.ArgumentParser(description="Process positional arguments.")
    parser.add_argument("tf", type=str, help="Time frame")
    parser.add_argument(
        "numCandles", type=int, help="Number of candles worth of data to collect"
    )
    parser.add_argument(
        "numPages",
        type=int,
        nargs="?",
        default=1,
        help="Number of pages of data to collect",
    )
    parser.add_argument(
        "filename",
        type=str,
        nargs="?",
        default="bitcoin_data.json",
        help="Output file name",
    )

    args = parser.parse_args()
    validate_input(args)

    currentPage = 1
    data = []
    while currentPage <= args.numPages:
        if currentPage == 1:
            print("\nFetching Bitcoin historical price data...")
        newData = fetch_bitcoin_history(args.tf, args.numCandles, currentPage)["data"]
        get_datetimes(newData)

        data = data + newData

        print("Page", currentPage, "complete.")
        currentPage += 1

    time_value, unit = split_numbers_and_letters(args.tf)
    unit_string = get_time_unit(unit)

    save_to_json(data, args.filename)
    print(
        f"\n[{time_value} {unit_string}] historical price action data collected successfully."
    )
    print(
        f"\n{args.numCandles * args.numPages} data points saved to '{args.filename}'"
    )

    print("\nExiting...\n")


if __name__ == "__main__":
    Main()
