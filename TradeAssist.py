import pandas as pd
import json

from constants import DAYS_OF_THE_WEEK


def Main():
    # Set the column spacing to a higher value
    pd.set_option(
        "display.width", 5000
    )  # This is for controlling the overall width of the display
    pd.set_option("display.max_columns", None)  # To show all columns without truncation
    pd.set_option("display.max_colwidth", None)  # To avoid truncating column content

    # Load JSON manually
    with open("bitcoin_data.json", "r") as file:
        json_data = json.load(file)  # Load JSON into a Python dictionary

        # Convert to DataFrame
        df = pd.DataFrame(json_data)

        # Rename columns for clarity
        df.rename(
            columns={
                "t": "Timestamp",
                "o": "Open",
                "h": "High",
                "l": "Low",
                "c": "Close",
                "v": "Volume",
                "day": "Day",
            },
            inplace=True,
        )

        # Reorder columns for better readability
        df = df[
            ["Timestamp", "datetime", "Day", "Open", "High", "Low", "Close", "Volume"]
        ]

        # Sort data in chronological order
        df.sort_values(by="datetime", ascending=True, inplace=True)

        # Reset index
        df.reset_index(drop=True, inplace=True)

        # Convert 'datetime' column to datetime type
        df["datetime"] = pd.to_datetime(df["datetime"])

        # Extract week and year to group by week
        df["week"] = df["datetime"].dt.to_period("W")

        # Find the weekly high and low and their corresponding days
        weekly_high_day = df.loc[df.groupby("week")["High"].idxmax()][
            ["week", "Day", "High", "datetime"]
        ]
        weekly_low_day = df.loc[df.groupby("week")["Low"].idxmin()][
            ["week", "Day", "Low", "datetime"]
        ]

        # Merge high and low data
        weekly_high_low = pd.concat(
            [
                weekly_high_day[["week", "Day", "High"]],
                weekly_low_day[["week", "Day", "Low"]],
            ]
        )

        # Initialize a dictionary to store probabilities for each day of the week
        days_of_week = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        day_probability = {
            day: {"High_Probability": 0, "Low_Probability": 0} for day in days_of_week
        }

        # Calculate how many times the high or low occurred for each day
        for day in days_of_week:
            high_day_count = weekly_high_low[
                (weekly_high_low["Day"] == day) & (weekly_high_low["High"].notnull())
            ].shape[0]
            low_day_count = weekly_high_low[
                (weekly_high_low["Day"] == day) & (weekly_high_low["Low"].notnull())
            ].shape[0]

            # Calculate the percentage (probability) for the high and low
            high_prob = (high_day_count / len(df["week"].unique())) * 100
            low_prob = (low_day_count / len(df["week"].unique())) * 100

            # Calculate total probability (just sum high and low probabilities)
            total_prob = (high_prob + low_prob) / 2

            # Store the combined result in the dictionary
            day_probability[day] = {
                "High_Probability": f"{high_prob:.2f}%",
                "Low_Probability": f"{low_prob:.2f}%",
                "Total_Probability": f"{total_prob:.2f}%",
            }

        # Convert the dictionary to a DataFrame for better readability
        day_probability_df = pd.DataFrame(day_probability).T

        # Display the DataFrame with combined daily probabilities and total probability
        print("\n\nChances of high or low occurring on a specific day:\n\n")
        print(day_probability_df)

        # Extract the week and year to group by week
        df["week"] = df["datetime"].dt.to_period("W")

        # Find the weekly high and low and their corresponding days and hours
        weekly_high_day = df.loc[df.groupby("week")["High"].idxmax()][
            ["week", "Day", "High", "datetime"]
        ]
        weekly_low_day = df.loc[df.groupby("week")["Low"].idxmin()][
            ["week", "Day", "Low", "datetime"]
        ]

        # Add an "hour" column to each
        weekly_high_day["Hour"] = weekly_high_day["datetime"].dt.hour
        weekly_low_day["Hour"] = weekly_low_day["datetime"].dt.hour

        # Merge the high and low day/hour data
        weekly_high_low = pd.concat(
            [
                weekly_high_day[["week", "Day", "High", "Hour"]],
                weekly_low_day[["week", "Day", "Low", "Hour"]],
            ]
        )

        # Initialize a dictionary to store probabilities for each hour
        hourly_probability = {}

        # Define the range of hours you want to check (e.g., from 0 to 23 for all hours of the day)
        for hour in range(24):
            # Count how many times the high occurred at this hour
            high_hour_count = weekly_high_low[
                (weekly_high_low["Hour"] == hour) & (weekly_high_low["High"].notnull())
            ].shape[0]

            # Count how many times the low occurred at this hour
            low_hour_count = weekly_high_low[
                (weekly_high_low["Hour"] == hour) & (weekly_high_low["Low"].notnull())
            ].shape[0]

            # Calculate the percentage (probability) for the high and low
            high_prob = (high_hour_count / len(df["week"].unique())) * 100
            low_prob = (low_hour_count / len(df["week"].unique())) * 100

            # Calculate total probability (sum of high and low probabilities)
            total_prob = (high_prob + low_prob) / 2

            # Store the combined result in the dictionary
            hourly_probability[hour] = {
                "High_Probability": f"{high_prob:.2f}%",
                "Low_Probability": f"{low_prob:.2f}%",
                "Total_Probability": f"{total_prob:.2f}%",
            }

        # Convert the dictionary to a DataFrame for better readability
        hourly_probability_df = pd.DataFrame.from_dict(
            hourly_probability, orient="index"
        )

        # Display the DataFrame with hourly probabilities
        print(
            "\n\nChances of high or low occurring within a specific hour of the day:\n\n"
        )
        print(hourly_probability_df)
        print("\n\n")

        # Convert 'datetime' column to datetime type
        df['datetime'] = pd.to_datetime(df['datetime'])

        # Extract relevant features
        df['day'] = df['datetime'].dt.day_name()  # Day name (e.g., Monday, Tuesday)
        df['hour'] = df['datetime'].dt.hour       # Extract hour
        df['week'] = df['datetime'].dt.isocalendar().week  # Get ISO week number
        df['year'] = df['datetime'].dt.year       # Extract year

        # Initialize lists to store weekly high/low occurrences
        weekly_highs = []
        weekly_lows = []

        # Group by each week to find the weekly high and low
        for (year, week), week_data in df.groupby(['year', 'week']):
            week_high = week_data.loc[week_data['High'].idxmax()]
            week_low = week_data.loc[week_data['Low'].idxmin()]
            
            # Store day and hour of high and low
            weekly_highs.append({'Day': week_high['day'], 'Hour': week_high['hour']})
            weekly_lows.append({'Day': week_low['day'], 'Hour': week_low['hour']})

        # Convert lists to DataFrames
        high_df = pd.DataFrame(weekly_highs)
        low_df = pd.DataFrame(weekly_lows)

        # Count occurrences of highs and lows per (Day, Hour) combination
        high_counts = high_df.value_counts().reset_index()
        low_counts = low_df.value_counts().reset_index()

        # Rename columns
        high_counts.columns = ['Day', 'Hour', 'High_Count']
        low_counts.columns = ['Day', 'Hour', 'Low_Count']

        # Merge counts and fill missing values with 0
        probability_df = pd.merge(high_counts, low_counts, on=['Day', 'Hour'], how='outer').fillna(0)

        # Calculate probabilities
        total_weeks = df['week'].nunique()
        probability_df['High_Probability'] = (probability_df['High_Count'] / total_weeks) * 100
        probability_df['Low_Probability'] = (probability_df['Low_Count'] / total_weeks) * 100
        probability_df['Total_Probability'] = (probability_df['High_Probability'] + probability_df['Low_Probability']) / 2

        # Sort values by probability
        probability_df = probability_df.sort_values(by=['Day', 'Total_Probability'], ascending=[True, False])

        # Select the top 5 hours for each day
        top_5_hours_per_day = probability_df.groupby('Day').head(5)

        # Print the result
        print(top_5_hours_per_day)


if __name__ == "__main__":
    Main()
