import numpy as np
import pandas as pd

import time
import os

from . import coeficient_creation_functions as coef_func
from analyzer import models

def create_pilot_rating ():
    st_t = time.perf_counter()

    individual_pilot_statistic_df = pd.DataFrame(
        {
            "pilot": pd.Series(dtype=str)
        }
    )
    
    races = models.VelikiPeregoni.objects.all()
    
    individual_pilot_statistic_df = pd.DataFrame(
        {
            "pilot": pd.Series(str)
        }
    )
    individual_pilot_statistic_df = individual_pilot_statistic_df.drop(0)
    
    for race in races:
        race_query = models.TempOfPilotsInVP.objects.filter(race = race.id).values_list()
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
        
        column_name = f"race_{race.id}"
        
        for pilot in race_statistic_df.loc[:, "pilot"]:
            lap_time = race_statistic_df.loc[
                race_statistic_df.loc[:, "pilot"] == pilot,
                "average_lap_time"
            ].reset_index(drop=True)
            needed_index = individual_pilot_statistic_df[
                (individual_pilot_statistic_df.loc[:,"pilot"] == pilot)
            ].index
            if not needed_index.empty:
                individual_pilot_statistic_df.loc[
                    needed_index,
                    column_name
                ] = lap_time[0]
            else:
                individual_pilot_statistic_df.loc[len(individual_pilot_statistic_df.index), "pilot"]=pilot
                individual_pilot_statistic_df.loc[
                    individual_pilot_statistic_df.loc[:, "pilot"] == pilot,
                    column_name
                ] = lap_time[0]
                
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