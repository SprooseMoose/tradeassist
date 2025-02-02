import pandas as pd
import json

from DataFrameUtils import (
    PrintAverageAndMedianWeeklyRange,
    PrintHighLowProbabilityByDay,
    PrintHighLowProbabilityByHour,
)
from utils import RenameColumns


def Main():
    # Load JSON manually
    with open("bitcoin_data.json", "r") as file:
        json_data = json.load(file)  # Load JSON into a Python dictionary
        # Convert to DataFrame
        df = pd.DataFrame(json_data)
        
        RenameColumns(df)

        # Sort data in chronological order
        df.sort_values(by="datetime", ascending=True, inplace=True)

        # Convert 'datetime' column to datetime type
        df["datetime"] = pd.to_datetime(df["datetime"])

        # Extract hour, week and year
        df["week"] = df["datetime"].dt.to_period("W")
        df["hour"] = df["datetime"].dt.hour

        PrintAverageAndMedianWeeklyRange(df)
        PrintHighLowProbabilityByDay(df)
        PrintHighLowProbabilityByHour(df)


if __name__ == "__main__":
    Main()
