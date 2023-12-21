import pandas as pd
import numpy as np

import time

from . import models_transmissions

from recorder import models as recorder_models


def does_race_has_true_karts(
    df_with_race_records: pd.DataFrame
):
    """
    Check if a race DataFrame contains records with 'true_kart' set to True.

    This function examines a DataFrame with race records and determines if there are records
    with the 'true_kart' column set to True.

    Parameters:
    - df_with_race_records (pd.DataFrame): The DataFrame containing race records.

    Returns:
    - bool: True if there are records with 'true_kart' set to True, False otherwise.

    Note:
    The function uses the value counts of the 'true_kart' column and checks if there are
    records with 'true_kart' set to True.
    """
    true_kart_count = df_with_race_records["true_kart"].value_counts()
    try:
        true_kart_count = true_kart_count[True]
        return True
    except KeyError:
        return False

def kart_column_into_str (
    kart: int
):
    """
    Convert an integer kart value into a string representation.

    This function takes an integer representing a kart number and converts it into a string
    representation. If the kart number is less than or equal to 9, a leading zero is added.

    Parameters:
    - kart (int): The integer kart number to be converted.

    Returns:
    - str: The string representation of the kart number.

    Note:
    If the kart number is greater than 9, the resulting string will be in the format "kart_N",
    where N is the kart number. If the kart number is 9 or less, a leading zero is added to the
    string representation.
    """
    if kart > 9:
        kart = "kart_" + str(kart)
    else:
        kart = "kart_0" + str(kart)
    return kart

def str_time_into_float_change(
    time_in_str: str
):
    """
    Convert a string representation of lap time into a float.

    This function takes a string representing lap time in the format "mm:ss" or a floating-point
    number and converts it into a float. If the input is a floating-point number, it is returned
    as is. If the input is in the "mm:ss" format, it is converted into seconds as a float.

    Parameters:
    - time_in_str (str): The string representation of lap time.

    Returns:
    - float: The lap time in seconds.

    Note:
    If the input is a floating-point number, it is returned as is. If the input is in the "mm:ss"
    format, it is converted into seconds as a float (e.g., "1:30" becomes 90.0 seconds).
    """
    try:
        time_in_str = float(time_in_str)
    except ValueError:
        split_lap_time = time_in_str.split(":")
        time_in_str = float(split_lap_time[0])*60+float(split_lap_time[1])
    return time_in_str   


def column_with_str_time_into_float_time (
    column_to_change: pd.Series
):
    """
    Convert a pandas Series with string lap time representations into floats.

    This function takes a pandas Series containing lap time values either as strings in the
    format "mm:ss" or as floating-point numbers. It converts the string representations into
    floats (in seconds) and returns the modified Series.

    Parameters:
    - column_to_change (pd.Series): The pandas Series with lap time values.

    Returns:
    - pd.Series: The modified Series with lap time values as floats (in seconds).

    Note:
    If the input Series contains lap time values in the "mm:ss" format, they are converted
    into seconds as floats. If the values are already floating-point numbers, they are returned
    as is.
    """
    try:
        column_to_change=pd.to_numeric(column_to_change)
    except ValueError:
        column_to_change.apply(str_time_into_float_change)
        
    return column_to_change


def create_df_from_recorded_records(
    race_id
):    
    """
    Create a DataFrame from recorded race records.

    This function collects race records from the 'RaceRecords' model with a given 'race_id'
    and creates a DataFrame. If the race records do not have 'true_kart' values, it sets the 'kart'
    column to the integer representation of the 'team' column. The resulting DataFrame is then
    processed, including converting lap time-related columns to float values in seconds.

    Parameters:
    - race_id: The identification number of the race.

    Returns:
    - pd.DataFrame: The DataFrame containing recorded race records.

    Note:
    The function uses the 'models_transmissions.collect_model_records_into_DataFrame' function
    to fetch race records from the 'RaceRecords' model.

    If the race records do not have 'true_kart' values, the 'kart' column is set to the integer
    representation of the 'team' column, and 'true_kart' is set to True.

    Lap time-related columns ('lap_time', 's1_time', 's2_time') are converted to float values
    representing seconds.

    The resulting DataFrame is ready for further analysis.
    """
    df_from_recorded_records = models_transmissions.collect_model_records_into_DataFrame(
        model = recorder_models.RaceRecords,
        inheritance_id = race_id,
        column_of_inheritance_id = "race",
            purge_models_technical_columns=True
    )
    
    if not does_race_has_true_karts(
        df_with_race_records=df_from_recorded_records
    ): 
        df_from_recorded_records["kart"] = df_from_recorded_records["team"].astype(int)
        df_from_recorded_records["true_kart"] = True
    

    df_from_recorded_records["kart"] = df_from_recorded_records["kart"].apply(
        kart_column_into_str
    )
    df_from_recorded_records["pilot_name"] = df_from_recorded_records["pilot_name"].str.strip()

    columns_to_change=[
            "lap_time",
            "s1_time",
            "s2_time",
        ]
    for column in columns_to_change:    
        df_from_recorded_records[column]=column_with_str_time_into_float_time(
            column_to_change=df_from_recorded_records[column]
        )
    del columns_to_change, race_id

    return df_from_recorded_records