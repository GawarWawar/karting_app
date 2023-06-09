import numpy as np
import pandas as pd

import time

import os

from utils import coeficient_creation_functions as coef_func

st_t = time.perf_counter()

individual_pilot_statistic_df = pd.DataFrame(
    {
        "pilot": pd.Series(dtype=str)
    }
)

path_to_records = "data/temp_by_races"
files_to_read = os.listdir(path_to_records)
files_to_read.reverse()
dict_of_df_of_races = {}
for race_numbe_file_tuple in enumerate(files_to_read):
    try:
        race_statistic_df = pd.read_csv(
            path_to_records+"/"+race_numbe_file_tuple[1],
            dtype={
                "pilot": str,
                "lap_time": float,
            }
        )
        
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
            lap_time = race_statistic_df.loc[
                    race_statistic_df.loc[:, "pilot"] == pilot,
                    "lap_time"
                ]
            lap_time = lap_time.values
            individual_pilot_statistic_df.loc[
                individual_pilot_statistic_df.loc[:, "pilot"] == pilot,
                f"race_{race_numbe_file_tuple[0]+1}"
            ] = lap_time
        
    except pd.errors.EmptyDataError:
        pass

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
individual_pilot_statistic_df.to_csv("data/pilot_rating.csv", index=False, index_label=False)

en_t = time.perf_counter()
print(en_t-st_t)