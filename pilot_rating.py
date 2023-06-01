import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from dateutil import parser

import time

import sys
import os

from sklearn.preprocessing import Normalizer

individual_pilot_names_df = pd.DataFrame(
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
        
        individual_pilot_names_df = pd.concat(
            [
                individual_pilot_names_df,
                df_pilots_to_concate
            ]
        )
        
        individual_pilot_names_df = individual_pilot_names_df.drop_duplicates(
            "pilot",ignore_index=True, keep="first"
        )
        
        for pilot in race_statistic_df.loc[:, "pilot"]:
            lap_time = race_statistic_df.loc[
                    race_statistic_df.loc[:, "pilot"] == pilot,
                    "lap_time"
                ]
            lap_time = lap_time.values
            individual_pilot_names_df.loc[
                individual_pilot_names_df.loc[:, "pilot"] == pilot,
                f"race_{race_numbe_file_tuple[0]+1}"
            ] = lap_time
        
    except pd.errors.EmptyDataError:
        pass
 
        
individual_pilot_names_df.to_csv("test.csv")

pilots_records_in_VP_df = pd.read_csv(
    "pilot_rating.csv",
    dtype={
        "pilot": str,
        "lap_time": float
    }
)

pilots_mean_time_across_all_VP_df = pilots_records_in_VP_df.loc[:, "pilot"].drop_duplicates().copy().T.to_frame().reset_index(drop=True)
for pilot in pilots_mean_time_across_all_VP_df.loc[:, "pilot"]:
    pilots_mean_time_across_all_VP_df.loc[
        pilots_mean_time_across_all_VP_df.loc[:, "pilot"] == pilot,
        "temp"    
    ] = pilots_records_in_VP_df.loc[
            pilots_records_in_VP_df.loc[:, "pilot"] == pilot, 
            "lap_time"
        ].mean()

pilots_mean_time_across_all_VP_df["normilized_temp"] = pilots_mean_time_across_all_VP_df["temp"].copy()
max_temp = pilots_mean_time_across_all_VP_df.loc[:, "normilized_temp"].max()
min_temp = pilots_mean_time_across_all_VP_df.loc[:, "normilized_temp"].min()

for temp in range(0, len(pilots_mean_time_across_all_VP_df.loc[:, "normilized_temp"])):
    normilezed_temp = (pilots_mean_time_across_all_VP_df.loc[temp, "normilized_temp"]-min_temp)/(max_temp-min_temp)
    pilots_mean_time_across_all_VP_df.loc[temp, "normilized_temp"] = normilezed_temp
    
pilots_mean_time_across_all_VP_df.sort_values(by="normilized_temp",inplace=True,ignore_index=True)

#pilots_mean_time_across_all_VP_df = pilots_mean_time_across_all_VP_df.values
#norm = Normalizer(norm="max")
#pilots_mean_time_across_all_VP_df[:, 1] = norm.fit_transform([pilots_mean_time_across_all_VP_df[:, 1]])

