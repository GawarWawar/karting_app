import pandas as pd
import numpy as np

import time

from recorder import models as recorder_models


def collect_race_records_into_DataFrame (
    race_id
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

    # Delete stuff from model, that is wont be used
    df_from_recorded_records.pop("id")
    df_from_recorded_records.pop("race")
    
    return df_from_recorded_records