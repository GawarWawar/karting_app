import numpy as np
import pandas as pd

import time

import os

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
        max_temp = individual_pilot_statistic_df.loc[:, race_as_column].max()
        min_temp = individual_pilot_statistic_df.loc[:, race_as_column].min()
        for temp in range(len(individual_pilot_statistic_df.loc[:, race_as_column])):
            normilezed_temp =(
                (individual_pilot_statistic_df.loc[temp, race_as_column]-min_temp)
                /
                (max_temp-min_temp)
            )
            normilezed_temp = float(f"{normilezed_temp:.4f}")
            individual_pilot_statistic_df.loc[temp, race_as_column] = normilezed_temp

for index in individual_pilot_statistic_df.loc[:, "pilot"].index:
    average_pilot_coeficient = individual_pilot_statistic_df.iloc[index, 1:-1].mean()
    average_pilot_coeficient = float(f"{average_pilot_coeficient:.4f}")
    individual_pilot_statistic_df.loc[index, "coeficient"] = average_pilot_coeficient

individual_pilot_statistic_df.to_csv("test.csv", index=False, index_label=False)

