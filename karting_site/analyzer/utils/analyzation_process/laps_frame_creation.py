import pandas as pd
import numpy as np

import time

from . import models_transmissions

from recorder import models as recorder_models


def does_race_has_true_karts(
    df_with_race_records: pd.DataFrame
):
    true_kart_count = df_with_race_records["true_kart"].value_counts()
    try:
        true_kart_count = true_kart_count[True]
        return True
    except KeyError:
        return False

def kart_column_into_str (
    kart: int
):
    if kart > 9:
        kart = "kart_" + str(kart)
    else:
        kart = "kart_0" + str(kart)
    return kart

def str_time_into_float_change(
    time_in_str: str
):
    try:
        time_in_str = float(time_in_str)
    except ValueError:
        split_lap_time = time_in_str.split(":")
        time_in_str = float(split_lap_time[0])*60+float(split_lap_time[1])
    return time_in_str   


def column_with_str_time_into_float_time (
    column_to_change: pd.Series
):
    try:
        column_to_change=pd.to_numeric(column_to_change)
    except ValueError:
        column_to_change.apply(str_time_into_float_change)
        
    return column_to_change


def create_df_from_recorded_records(
    race_id
):    
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