import pandas as pd
import numpy as np

import time


def mark_rows_with_wrong_string_in_column(
    column_item: str,
    wrong_string_to_look_for: str,
):
    if wrong_string_to_look_for in column_item:
        return True
    else:
        return False

def clear_column_from_unneeded_strings (
    df_to_clear: pd.DataFrame,
    
    column_to_look_into: str,
    wrong_string_to_look_for: str
):
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
    mean_lap_time = df_with_race_records.loc[:, "lap_time"].mean()
    laps_to_delete = df_with_race_records.loc[
        df_with_race_records.loc[:, "lap_time"] < mean_lap_time+margin_to_add_to_mean_time, 
        "lap_time"
    ].index
    df_with_race_records.drop(laps_to_delete)
    del mean_lap_time, margin_to_add_to_mean_time
    
    return df_with_race_records
