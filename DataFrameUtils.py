import pandas as pd
from constants import DAYS_OF_THE_WEEK


def GetFrequentHighLowByHour(df, filterFirst):
    # Convert 'datetime' column to datetime type
    df["datetime"] = pd.to_datetime(df["datetime"])
    # Extract relevant features
    df["hour"] = df["datetime"].dt.hour  # Extract hour
    df["week"] = df["datetime"].dt.isocalendar().week  # Get ISO week number
    df["year"] = df["datetime"].dt.year  # Extract year

    # Initialize lists to store weekly high/low occurrences
    weekly_highs = []
    weekly_lows = []
    # Group by each week to find the weekly high and low
    for (year, week), week_data in df.groupby(["year", "week"]):
        week_high = week_data.loc[week_data["high"].idxmax()]
        week_low = week_data.loc[week_data["low"].idxmin()]

        # Store day and hour of high and low
        weekly_highs.append({"day": week_high["day"], "Hour": week_high["hour"]})
        weekly_lows.append({"day": week_low["day"], "Hour": week_low["hour"]})
    # Convert lists to DataFrames
    high_df = pd.DataFrame(weekly_highs)
    low_df = pd.DataFrame(weekly_lows)
    # Count occurrences of highs and lows per (day, Hour) combination
    high_counts = high_df.value_counts().reset_index()
    low_counts = low_df.value_counts().reset_index()
    # Rename columns
    high_counts.columns = ["day", "Hour", "high_Count"]
    low_counts.columns = ["day", "Hour", "low_Count"]
    # Merge counts and fill missing values with 0
    probability_df = pd.merge(
        high_counts, low_counts, on=["day", "Hour"], how="outer"
    ).fillna(0)
    # Calculate probabilities
    total_weeks = df["week"].nunique()
    probability_df["high_probability"] = (
        probability_df["high_Count"] / total_weeks
    ) * 100
    probability_df["low_probability"] = (
        probability_df["low_Count"] / total_weeks
    ) * 100
    probability_df["total_probability"] = (
        probability_df["high_probability"] + probability_df["low_probability"]
    ) / 2
    # Sort values by probability
    probability_df = probability_df.sort_values(
        by=["day", "total_probability"], ascending=[True, False]
    )
    # Select the top 5 hours for each day
    return probability_df.groupby("day").head(filterFirst)


def GetAverageAndMedianWeeklyRange(df):
    # Extract the week and year to group by week
    df["week"] = df["datetime"].dt.to_period("W")
    # Convert 'datetime' column to datetime type
    df["datetime"] = pd.to_datetime(df["datetime"])
    # Extract relevant features
    df["hour"] = df["datetime"].dt.hour  # Extract hour
    df["year"] = df["datetime"].dt.year  # Extract year
    # Group data by (year, week) and calculate weekly high, weekly low, and price range
    weekly_ranges = (
        df.groupby(["year", "week"])
        .agg(weekly_high=("high", "max"), weekly_low=("low", "min"))
        .reset_index()
    )
    # Calculate the price difference between weekly high and low
    weekly_ranges["range"] = (
        weekly_ranges["weekly_high"] - weekly_ranges["weekly_low"]
    )
    # Rename columns to lowercase
    weekly_ranges.columns = [
        "year",
        "week",
        "weekly_high",
        "weekly_low",
        "range",
    ]
    # Compute the average price difference across all weeks
    average_range = weekly_ranges["range"].mean()
    median_range = weekly_ranges["range"].median()
    return average_range, median_range


def PrintAverageAndMedianWeeklyRange(df):
    average, median = GetAverageAndMedianWeeklyRange(df)

    # Print results
    print(f"\nAverage weekly price difference: {average:.2f}")
    print(f"\nMedian weekly price difference: {median:.2f}")


def GetHighLowProbabilityByHour(df):
    # Extract the week and year to group by week
    df["week"] = df["datetime"].dt.to_period("W")
    # Convert 'datetime' column to datetime type
    df["datetime"] = pd.to_datetime(df["datetime"])
    # Extract relevant features
    df["hour"] = df["datetime"].dt.hour  # Extract hour
    df["year"] = df["datetime"].dt.year  # Extract year

    # Find the weekly high and low and their corresponding days and hours
    weekly_high_day = df.loc[df.groupby("week")["high"].idxmax()][
        ["week", "day", "high", "datetime"]
    ]
    weekly_low_day = df.loc[df.groupby("week")["low"].idxmin()][
        ["week", "day", "low", "datetime"]
    ]

    # Add an "hour" column to each
    weekly_high_day["Hour"] = weekly_high_day["datetime"].dt.hour
    weekly_low_day["Hour"] = weekly_low_day["datetime"].dt.hour

    # Merge the high and low day/hour data
    weekly_high_low = pd.concat(
        [
            weekly_high_day[["week", "day", "high", "Hour"]],
            weekly_low_day[["week", "day", "low", "Hour"]],
        ]
    )

    # Initialize a dictionary to store probabilities for each hour
    hourly_probability = {}

    # Define the range of hours you want to check (e.g., from 0 to 23 for all hours of the day)
    for hour in range(24):
        # Count how many times the high occurred at this hour
        high_hour_count = weekly_high_low[
            (weekly_high_low["Hour"] == hour) & (weekly_high_low["high"].notnull())
        ].shape[0]

        # Count how many times the low occurred at this hour
        low_hour_count = weekly_high_low[
            (weekly_high_low["Hour"] == hour) & (weekly_high_low["low"].notnull())
        ].shape[0]

        # Calculate the percentage (probability) for the high and low
        high_prob = (high_hour_count / len(df["week"].unique())) * 100
        low_prob = (low_hour_count / len(df["week"].unique())) * 100

        # Calculate total probability (sum of high and low probabilities)
        total_prob = (high_prob + low_prob) / 2

        # Store the combined result in the dictionary
        hourly_probability[hour] = {
            "high_probability": f"{high_prob:.2f}%",
            "low_probability": f"{low_prob:.2f}%",
            "total_probability": f"{total_prob:.2f}%",
        }

    # Convert the dictionary to a DataFrame for better readability
    return pd.DataFrame.from_dict(hourly_probability, orient="index")


def GetHighLowProbabilityByDay(df):
    # Find the weekly high and low and their corresponding days
    weekly_high_day = df.loc[df.groupby("week")["high"].idxmax()][
        ["week", "day", "high", "datetime"]
    ]
    weekly_low_day = df.loc[df.groupby("week")["low"].idxmin()][
        ["week", "day", "low", "datetime"]
    ]
    # Merge high and low data
    weekly_high_low = pd.concat(
        [
            weekly_high_day[["week", "day", "high"]],
            weekly_low_day[["week", "day", "low"]],
        ]
    )
    day_probability = {
        day: {"high_probability": 0, "low_probability": 0} for day in DAYS_OF_THE_WEEK
    }
    # Calculate how many times the high or low occurred for each day
    for day in DAYS_OF_THE_WEEK:
        high_day_count = weekly_high_low[
            (weekly_high_low["day"] == day) & (weekly_high_low["high"].notnull())
        ].shape[0]
        low_day_count = weekly_high_low[
            (weekly_high_low["day"] == day) & (weekly_high_low["low"].notnull())
        ].shape[0]
        # Calculate the percentage (probability) for the high and low
        high_prob = (high_day_count / len(df["week"].unique())) * 100
        low_prob = (low_day_count / len(df["week"].unique())) * 100
        # Calculate total probability (just sum high and low probabilities)
        total_prob = (high_prob + low_prob) / 2
        # Store the combined result in the dictionary
        day_probability[day] = {
            "high_probability": f"{high_prob:.2f}%",
            "low_probability": f"{low_prob:.2f}%",
            "total_probability": f"{total_prob:.2f}%",
        }
    # Convert the dictionary to a DataFrame for better readability
    return pd.DataFrame(day_probability).T


def PrintHighLowProbabilityByDay(df):
    print(
        "\nChances of high or low occurring on a specific day:\n\n",
        GetHighLowProbabilityByDay(df),
    )


def PrintHighLowProbabilityByHour(df):
    print(
        "\nChances of high or low occurring within a specific hour of the day:\n\n",
        GetHighLowProbabilityByHour(df),
    )


def PrintFrequentHighLowByHour(df):
    print(
        "\nFrequency of daily high or low occurences by hour:\n\n",
        GetFrequentHighLowByHour(df),
    )
