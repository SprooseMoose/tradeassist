import requests
import argparse
from utils import split_numbers_and_letters, get_time_unit, get_datetimes, save_to_json
from constants import TIME_FRAMES


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


def fetch_bitcoin_history(tf, numCandles, currentPage):
    url = f"https://api.finazon.io/latest/finazon/crypto/time_series?ticker=BTC/USDT&interval={tf}&page={currentPage}&page_size={numCandles}&apikey=27937194b05042048c1ddda8f2fd697dhk"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return data
    else:
        print("Failed to fetch data")
        return None


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
    print(f"\n{args.numCandles * args.numPages} data points saved to '{args.filename}'")

    print("\nExiting...\n")


if __name__ == "__main__":
    Main()
