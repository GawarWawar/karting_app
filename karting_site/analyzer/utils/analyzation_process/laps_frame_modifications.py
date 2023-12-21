import pandas as pd
import numpy as np

import time


def mark_rows_with_wrong_string_in_column(
    column_item: str,
    wrong_string_to_look_for: str,
):
    """
    Mark rows based on the presence of a wrong string in a given column item.

    This function checks if a specified wrong string is present in a given column item.
    If the wrong string is found, the function returns True, indicating that the row should be marked.

    Parameters:
    - column_item (str): The string value in the column to check.
    - wrong_string_to_look_for (str): The wrong string to search for in the column item.

    Returns:
    - bool: True if the wrong string is found, False otherwise.
    """
    if wrong_string_to_look_for in column_item:
        return True
    else:
        return False

def clear_column_from_unneeded_strings (
    df_to_clear: pd.DataFrame,
    
    column_to_look_into: str,
    wrong_string_to_look_for: str
):
    """
    Clear a DataFrame column from rows containing specified wrong strings.

    This function filters a DataFrame based on the presence of a specified wrong string
    in a particular column. Rows containing the wrong string are removed from the DataFrame.

    Parameters:
    - df_to_clear (pd.DataFrame): The DataFrame to be cleared.
    - column_to_look_into (str): The name of the column to check for wrong strings.
    - wrong_string_to_look_for (str): The wrong string to search for in the specified column.

    Returns:
    - pd.DataFrame: The DataFrame with rows containing the wrong string removed.

    Note:
    The function uses boolean indexing to filter rows based on the presence of the specified
    'wrong_string_to_look_for' in the specified 'column_to_look_into'. Rows containing the
    wrong string are removed from the DataFrame, and the cleaned DataFrame is returned.
    """
    # Use boolean indexing to filter rows to delete
    delete_mask = df_to_clear[column_to_look_into].apply(
        mark_rows_with_wrong_string_in_column,
        wrong_string_to_look_for = wrong_string_to_look_for,
    )
    
    # Invert delete_mask with ~ to keep rows with good names
    df_to_clear = df_to_clear[~delete_mask]
    
    return df_to_clear   


def clear_outstanding_laps (
    df_with_race_records: pd.DataFrame,
    margin_to_add_to_mean_time: int = 5, # Time in seconds
):
    """
    Clear outstanding laps from a DataFrame based on lap time.

    This function calculates the mean lap time from a DataFrame and removes rows with lap times
    significantly longer than the mean time plus a specified margin in seconds.

    Parameters:
    - df_with_race_records (pd.DataFrame): The DataFrame containing race records.
    - margin_to_add_to_mean_time (int): The margin in seconds to add to the mean lap time.
      Default is 5 seconds.

    Returns:
    - pd.DataFrame: The DataFrame with outstanding laps removed.

    Note:
    The function calculates the mean lap time from the 'lap_time' column in the DataFrame.
    Rows with lap times significantly longer than the mean time plus the specified margin
    are removed from the DataFrame. The cleaned DataFrame is then returned.
    """
    mean_lap_time = df_with_race_records.loc[:, "lap_time"].mean()
    laps_to_delete = df_with_race_records.loc[
        df_with_race_records.loc[:, "lap_time"] < mean_lap_time+margin_to_add_to_mean_time, 
        "lap_time"
    ].index
    df_with_race_records.drop(laps_to_delete)
    del mean_lap_time, margin_to_add_to_mean_time
    
    return df_with_race_records
