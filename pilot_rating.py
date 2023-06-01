import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from dateutil import parser

import time

import sys
import os

from sklearn.preprocessing import Normalizer

path_to_records = "data/temp_by_races"
files_to_read = os.listdir(path_to_records)
dict_of_df_of_races = {}
for file in enumerate(files_to_read):
    try:
        df_to_add = pd.read_csv(
            path_to_records+"/"+file[1],
            dtype={
                "team": int,
                "pilot": str,
                "kart": int,
                "lap": int,
                "lap_time": float,
                "s1": float,
                "s2": float,
                "segment": int,
                "true_name": bool,
                "true_kart": bool,
            }
        )
        
        dict_with_df_to_add = {
            file[0]: df_to_add
        }
        
        dict_of_df_of_races.update(dict_with_df_to_add)
    except pd.errors.EmptyDataError:
        pass

individual_pilot_names_df = pd.DataFrame(
    {
        "pilot": pd.Series(dtype=str)
    }
)
for df in dict_of_df_of_races:
    df_to_concate = dict_of_df_of_races[df].loc[:, "pilot"].T.to_frame().copy()
    individual_pilot_names_df = pd.concat(
        [
            individual_pilot_names_df,
            df_to_concate
        ]
    )

individual_pilot_names_df = individual_pilot_names_df.drop_duplicates(ignore_index=True)

for df in range(len(dict_of_df_of_races)):
    individual_pilot_names_df[f"race_{df+1}"] = np.nan
    for pilot in dict_of_df_of_races[df].loc[:, "pilot"]:
        lap_time = dict_of_df_of_races[df].loc[
                dict_of_df_of_races[df].loc[:, "pilot"] == pilot,
                "lap_time"
            ]
        if not lap_time.empty:
            lap_time = lap_time.values
            individual_pilot_names_df.loc[
                individual_pilot_names_df.loc[:, "pilot"] == pilot,
                f"race_{df}"
            ] = lap_time
        
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

