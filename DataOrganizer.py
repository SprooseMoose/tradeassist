from datetime import timedelta, datetime
import json
from utils import save_to_json


def group_by_week_starting_monday(data):
    weekly_data = {}

    for candle in data:
        # Convert Unix timestamp to date
        date = datetime.fromtimestamp(candle["t"])

        # Find the Monday of that week
        week_start = get_week_start(date).strftime("%Y-%m-%d")  # Format as YYYY-MM-DD

        # Group by week start date
        if week_start not in weekly_data:
            weekly_data[week_start] = []  # Initialize list if not present

        weekly_data[week_start].append(candle)

    return weekly_data


# Function to get the Monday of the same week for a given date
def get_week_start(date):
    return date - timedelta(days=date.weekday())  # Monday of that week


def Main():
    print("Loading json data...")
    
    with open("bitcoin_data.json", "r") as file:
        data = json.load(file)
        
    print("Sorting by week starting Monday..")

    weekly_data = group_by_week_starting_monday(data)

    save_to_json(weekly_data, "weekly_data.json")
    
    print("Data groupings complete.")


if __name__ == "__main__":
    Main()