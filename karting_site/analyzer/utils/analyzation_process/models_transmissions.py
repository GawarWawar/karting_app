import pandas as pd
import numpy as np

import time

from recorder import models as recorder_models
from analyzer import models as analyzer_models

def collect_race_records_into_DataFrame (
    race_id: int,
    purge_models_technical_columns:bool = True
):
    race = recorder_models.Race.objects.get(pk = race_id)
    race_records = recorder_models.RaceRecords.objects.filter(race = race).values_list()
    del race
    df_from_recorded_records = pd.DataFrame.from_records(
        race_records,
        columns=[
            "id",
            "race",
            "team",
            "pilot",
            "kart",
            "lap",
            "lap_time",
            "s1",
            "s2",
            "segment",
            "true_name",
            "true_kart",
        ]
    )
    del race_records

    if purge_models_technical_columns:
        # Delete columns from model
        df_from_recorded_records.pop("id")
        df_from_recorded_records.pop("race")
    
    return df_from_recorded_records

def collect_BR_temp_records_into_DataFrame (
    race_id: int,
    purge_models_technical_columns:bool = True
):
    big_race = analyzer_models.TempOfPilotsInBR.objects.filter(race = race_id).values_list()
    df_of_race_temps = pd.DataFrame.from_records(
        big_race, 
        columns=[
            "id",
            "race",
            "pilot",
            "average_lap_time"
        ]
    )
    
    if purge_models_technical_columns:
        # Delete columns from model
        df_of_race_temps.pop("id")
        df_of_race_temps.pop("race")
    
    return df_of_race_temps