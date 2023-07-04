import numpy as np
import pandas as pd

import time
import os

from .utils import coeficient_creation_functions as coef_func
from . import models

def create_pilot_rating ():
    st_t = time.perf_counter()

    individual_pilot_statistic_df = pd.DataFrame(
        {
            "pilot": pd.Series(dtype=str)
        }
    )

    path_to_records = "analyzer/data/temp_by_races"
    files_to_read = os.listdir(path_to_records)
    files_to_read.reverse()
    
    races = models.VelikiPeregoni.objects.all()
    
    for race in races:
        race_query = models.PilotsInVP.objects.filter(race = race.id).values_list()
        race_statistic_df = pd.DataFrame.from_records(
            race_query, 
            columns=[
                "id",
                "race_id",
                "pilot",
                "average_lap_time"
            ]
        )
       
        
        race_statistic_df.pop("id")
        race_statistic_df.pop("race_id")

        df_pilots_to_concate = pd.DataFrame(
            {
                "pilot": race_statistic_df["pilot"].copy()
            }
        )
        
        individual_pilot_statistic_df = pd.concat(
            [
                individual_pilot_statistic_df,
                df_pilots_to_concate
            ]
        )
        
        individual_pilot_statistic_df = individual_pilot_statistic_df.drop_duplicates(
            "pilot",ignore_index=True, keep="first"
        )
        
        for pilot in race_statistic_df.loc[:, "pilot"]:
            needed_index = race_statistic_df.loc[race_statistic_df.loc[:, "pilot"] == pilot, "pilot"].index
            lap_time = race_statistic_df.at[
                needed_index[0],
                "average_lap_time"
            ]
            
            individual_pilot_statistic_df.loc[
                individual_pilot_statistic_df.loc[:, "pilot"] == pilot,
                race.id
            ] = lap_time

    for race_as_column in individual_pilot_statistic_df:
        if race_as_column != "pilot":
            individual_pilot_statistic_df[race_as_column] =\
                coef_func.column_with_lap_time_to_coeficient(
                    individual_pilot_statistic_df.loc[:,race_as_column].copy()
                )

    for index in individual_pilot_statistic_df.loc[:, "pilot"].index:
        average_pilot_coeficient = individual_pilot_statistic_df.iloc[index, 1:-1].mean()
        average_pilot_coeficient = float(f"{average_pilot_coeficient:.4f}")
        individual_pilot_statistic_df.loc[index, "coeficient"] = average_pilot_coeficient

    individual_pilot_statistic_df = pd.DataFrame(
        {
            "pilot": individual_pilot_statistic_df["pilot"],
            "coeficient": individual_pilot_statistic_df["coeficient"]
        }
    )

    en_t = time.perf_counter()
    print(en_t-st_t)
    return individual_pilot_statistic_df