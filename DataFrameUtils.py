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
    weekly_ranges["range"] = weekly_ranges["weekly_high"] - weekly_ranges["weekly_low"]
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


def GetHighLowProbabilityByHour(df, topn=12):
    # Convert 'datetime' column to datetime type if not already
    df["datetime"] = pd.to_datetime(df["datetime"])
    
    # Extract the week and year to group by week
    df["week"] = df["datetime"].dt.to_period("W")
    
    # Extract relevant features
    df["hour"] = df["datetime"].dt.hour  # Extract hour

    # Group by hour and calculate the average volume
    hourly_avg_volume = df.groupby("hour")["volume"].mean().reset_index()

    # Round to two decimal places for better readability
    hourly_avg_volume["volume"] = hourly_avg_volume["volume"].round(2)

    # Find the weekly high and low and their corresponding days and hours
    weekly_high_day = df.loc[df.groupby("week")["high"].idxmax()][["week", "day", "high", "datetime"]]
    weekly_low_day = df.loc[df.groupby("week")["low"].idxmin()][["week", "day", "low", "datetime"]]

    # Add an "hour" column to each
    weekly_high_day["hour"] = weekly_high_day["datetime"].dt.hour
    weekly_low_day["hour"] = weekly_low_day["datetime"].dt.hour

    # Merge the high and low day/hour data
    weekly_high_low = pd.concat(
        [
            weekly_high_day[["week", "day", "high", "hour"]],
            weekly_low_day[["week", "day", "low", "hour"]],
        ]
    )

    # Initialize a dictionary to store probabilities for each hour
    hourly_probability = {}

    # Define the range of hours you want to check (0 to 23 for all hours of the day)
    for hour in range(24):
        # Count occurrences of high and low at this hour
        high_hour_count = weekly_high_low[(weekly_high_low["hour"] == hour) & (weekly_high_low["high"].notnull())].shape[0]
        low_hour_count = weekly_high_low[(weekly_high_low["hour"] == hour) & (weekly_high_low["low"].notnull())].shape[0]

        # Calculate probabilities
        high_prob = (high_hour_count / len(df["week"].unique())) * 100
        low_prob = (low_hour_count / len(df["week"].unique())) * 100

        # Calculate total probability (sum of high and low probabilities)
        total_prob = high_prob + low_prob

        # Store the result
        hourly_probability[hour] = {
            "high_probability_%": round(high_prob, 2),
            "low_probability_%": round(low_prob, 2),
            "total_probability_%": round(total_prob, 2) / 2,
        }

    # Convert dictionary to DataFrame
    newFrame = pd.DataFrame.from_dict(hourly_probability, orient="index").reset_index()
    newFrame.rename(columns={"index": "hour"}, inplace=True)  # Rename index column to "hour"

    # Merge with the average volume DataFrame
    newFrame = pd.merge(newFrame, hourly_avg_volume, on="hour", how="left")
    
    new_order = ["volume", "hour"] + [col for col in newFrame.columns if col not in ["volume", "hour"]]

    # Reorder the DataFrame
    newFrame = newFrame[new_order]
    
    # Sort by highest average volume
    newFrame = newFrame.sort_values(by="high_probability_%", ascending=False)

    return newFrame


def GetHighLowProbabilityByDay(df):
    # Extract the week and year to group by week
    df["week"] = df["datetime"].dt.to_period("W")
    # Convert 'datetime' column to datetime type
    df["datetime"] = pd.to_datetime(df["datetime"])
    # Extract relevant features
    df["hour"] = df["datetime"].dt.hour  # Extract hour
    df["year"] = df["datetime"].dt.year  # Extract year
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


def GetTopHighLowProbabilityByHourAndDay(df, top_n=8):
    # Convert 'datetime' column to datetime type
    df["datetime"] = pd.to_datetime(df["datetime"])

    # Extract relevant time features
    df["week"] = df["datetime"].dt.to_period("W")  # Weekly grouping
    df["hour"] = df["datetime"].dt.hour  # Extract hour

    # Find the weekly high and low and their corresponding days and hours
    weekly_high_day = df.loc[df.groupby(["week"])["high"].idxmax()][
        ["week", "day", "high", "datetime"]
    ]
    weekly_low_day = df.loc[df.groupby(["week"])["low"].idxmin()][
        ["week", "day", "low", "datetime"]
    ]

    # Extract hour for high and low
    weekly_high_day["hour"] = weekly_high_day["datetime"].dt.hour
    weekly_low_day["hour"] = weekly_low_day["datetime"].dt.hour

    # Merge high and low data
    weekly_high_low = pd.concat(
        [
            weekly_high_day[["week", "day", "hour", "high"]],
            weekly_low_day[["week", "day", "hour", "low"]],
        ]
    )

    # Initialize dictionary to store probabilities
    hourly_day_probability = []

    # Loop through days and hours
    for day in df["day"].unique():
        for hour in range(24):
            # Count occurrences of highs and lows for each day-hour combination
            high_hour_count = weekly_high_low[
                (weekly_high_low["day"] == day)
                & (weekly_high_low["hour"] == hour)
                & (weekly_high_low["high"].notnull())
            ].shape[0]

            low_hour_count = weekly_high_low[
                (weekly_high_low["day"] == day)
                & (weekly_high_low["hour"] == hour)
                & (weekly_high_low["low"].notnull())
            ].shape[0]

            # Calculate probabilities
            total_weeks = len(df["week"].unique())
            high_prob = (high_hour_count / total_weeks) * 100
            low_prob = (low_hour_count / total_weeks) * 100
            total_prob = (high_prob + low_prob) / 2  # Averaged total probability

            # Store in list
            hourly_day_probability.append([day, hour, high_prob, low_prob, total_prob])

    # Convert list to DataFrame
    result_df = pd.DataFrame(
        hourly_day_probability,
        columns=[
            "day",
            "hour",
            "high_probability",
            "low_probability",
            "total_probability",
        ],
    )

    # Sort by day and then by total probability in descending order
    result_df = result_df.sort_values(
        by=["day", "total_probability"], ascending=[True, False]
    )

    # Keep only the **top N hours** for each day
    result_df = result_df.groupby("day").head(top_n)

    # Replace any 0% values with '-'
    result_df[["high_probability", "low_probability", "total_probability"]] = result_df[
        ["high_probability", "low_probability", "total_probability"]
    ].map(lambda x: "-" if x == 0 else f"{x:.2f}%")

    return result_df

def CountWeeklyHighLowOccurrences(df):
    # Convert 'datetime' column to datetime type
    df["datetime"] = pd.to_datetime(df["datetime"])

    # Extract week to group data
    df["week"] = df["datetime"].dt.to_period("W")

    # Find the weekly high and low and their corresponding days
    weekly_high_day = df.loc[df.groupby("week")["high"].idxmax()][["week", "day"]]
    weekly_low_day = df.loc[df.groupby("week")["low"].idxmin()][["week", "day"]]

    # Count occurrences separately for highs and lows
    high_counts = weekly_high_day["day"].value_counts().rename("high_occurrences")
    low_counts = weekly_low_day["day"].value_counts().rename("low_occurrences")

    # Combine both counts into a single table
    day_counts = pd.DataFrame({"high_occurrences": high_counts, "low_occurrences": low_counts, "total_occurences": high_counts + low_counts}).fillna(0).astype(int)
    
    # Reset index and rename for clarity
    day_counts = day_counts.reset_index().rename(columns={"index": "day"})

    # Add a day-of-week sorting key (Monday=0, Sunday=6)
    day_counts["day_order"] = day_counts["day"].apply(lambda x: DAYS_OF_THE_WEEK.index(x))

    # Sort by actual day of the week
    day_counts = day_counts.sort_values(by="day_order").drop(columns=["day_order"]).reset_index(drop=True)

    return day_counts

def GetHighestAvgVolumeHours(df, top_n=12):
    # Convert 'datetime' column to datetime type if not already
    if not pd.api.types.is_datetime64_any_dtype(df["datetime"]):
        df["datetime"] = pd.to_datetime(df["datetime"])

    # Extract the hour from timestamps
    df["hour"] = df["datetime"].dt.hour

    # Group by hour and calculate the average volume
    hourly_avg_volume = df.groupby("hour")["volume"].mean().reset_index()

    # Round to two decimal places for better readability
    hourly_avg_volume["volume"] = hourly_avg_volume["volume"].round(2)

    # Sort by highest average volume
    highest_avg_volume_hours = hourly_avg_volume.sort_values(by="volume", ascending=False).head(top_n)

    return highest_avg_volume_hours

def PrintGetHighestVolumeHours(df):
    print(
        "\nHighest cumulative volume per hour of the day:\n\n",
        GetHighestAvgVolumeHours(df).to_string(index=False),
    )

def PrintWeeklyHighLowOccurrences(df):
        print(
        "\nNumber of high or low occurring on each day:\n\n",
        CountWeeklyHighLowOccurrences(df),
    )

def PrintTopHighLowProbabilityByHourAndDay(df):
    print(
        "\nChances of high or low occurring on a specific day and hour:\n\n",
        GetTopHighLowProbabilityByHourAndDay(df),
    )


def PrintHighLowProbabilityByDay(df):
    print(
        "\nChances of high or low occurring on a specific day:\n\n",
        GetHighLowProbabilityByDay(df),
    )


def PrintHighLowProbabilityByHour(df):
    print(
        "\nChances of high or low occurring within a specific hour of the day:\n\n",
        GetHighLowProbabilityByHour(df).to_string(index=False),
    )


def PrintFrequentHighLowByHour(df):
    print(
        "\nFrequency of daily high or low occurences by hour:\n\n",
        GetFrequentHighLowByHour(df),
    )
