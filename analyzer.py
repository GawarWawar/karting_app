# FORMING DATABASE TO ANALIZE
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from dateutil import parser

import time

import sys
import os

from utils import analyzer_functions

import pprint

start = time.perf_counter()

competition = True

if competition:
    category = "kart"
else:
    category = "team"

df_from_recorded_records = pd.read_csv(
    "pilots_stats_template.csv",
    dtype={
        "team": int,
        "pilot": str,
        "kart": int,
        "lap": int,
        "lap_time": str,
        "s1": str,
        "s2": str,
        "segment": int,
        "true_name": bool,
        "true_kart": bool,
    }
)

path_to_records = "data/records"
files_to_read = os.listdir(path_to_records)
for file in files_to_read:
    try:
        df_to_concate = pd.read_csv(
            path_to_records+"/"+file,
            dtype={
                "team": int,
                "pilot": str,
                "kart": int,
                "lap": int,
                "lap_time": str,
                "s1": str,
                "s2": str,
                "segment": int,
                "true_name": bool,
                "true_kart": bool,
            }
        )
        df_from_recorded_records = pd.concat([df_from_recorded_records, df_to_concate], ignore_index=True)
    except pd.errors.EmptyDataError:
        pass

for i in range(len(df_from_recorded_records.loc[:,"lap_time"])):
    try:
        df_from_recorded_records.loc[i, "lap_time"] = float(df_from_recorded_records.iloc[i].at["lap_time"])
    except ValueError:
        split_lap_time = df_from_recorded_records.iloc[i].at["lap_time"].split(":")
        df_from_recorded_records.loc[i, "lap_time"] = float(split_lap_time[0])*60+float(split_lap_time[1])
        
    try:
        df_from_recorded_records.loc[i, "s2"] = float(df_from_recorded_records.iloc[i].at["s2"])
    except ValueError:
        split_lap_time = df_from_recorded_records.iloc[i].at["s2"].split(":")
        df_from_recorded_records.loc[i, "s2"] = float(split_lap_time[0])*60+float(split_lap_time[1])
        
    try:
        df_from_recorded_records.loc[i, "s1"] = float(df_from_recorded_records.iloc[i].at["s1"])
    except ValueError:
        split_lap_time = df_from_recorded_records.iloc[i].at["s1"].split(":")
        df_from_recorded_records.loc[i, "s1"] = float(split_lap_time[0])*60+float(split_lap_time[1])

df_from_recorded_records["lap_time"]=pd.to_numeric(df_from_recorded_records["lap_time"])
df_from_recorded_records["s2"]=pd.to_numeric(df_from_recorded_records["s2"])


df_pilots = df_from_recorded_records.loc[
    (df_from_recorded_records.loc[:, "true_name" ]== True), 
    "pilot"
].drop_duplicates().copy().T.to_frame()
df_pilots = df_pilots.reset_index(drop=True)
df_karts_and_pilots = df_from_recorded_records.loc[
    (df_from_recorded_records.loc[:, "true_name" ]== True), 
    #TESTING STUFF, ACTIVATE FOR RACE
    #and 
    #(df_from_recorded_records.loc[:, "true_kart" ]== True),
    ["pilot",category]
].drop_duplicates(keep="first").copy()

df_pilots["pilot_temp"] = 0
df_pilots["pilot_fastest_lap"] = 0
for pilot in df_pilots.loc[:, "pilot"]:
    all_pilot_records = df_from_recorded_records.loc[
            df_from_recorded_records.loc[:, "pilot"] == pilot,
            :
        ]
    
    df_pilots.loc[
        df_pilots.loc[:, "pilot"] == pilot,
        "pilot_temp"
    ] = all_pilot_records.loc[:, "lap_time"].mean()
    
    df_pilots.loc[
        df_pilots.loc[:, "pilot"] == pilot,
        "pilot_fastest_lap"
    ] = all_pilot_records.loc[:, "lap_time"].min()

df_karts_and_pilots["temp_with_pilot"] = 0
df_karts_and_pilots["fastest_lap_with_pilot"] = 0

for pilot in df_karts_and_pilots.loc[:, "pilot"]:
    all_pilot_kart_records = df_from_recorded_records.loc[
        df_from_recorded_records.loc[:, "pilot"]==pilot,
        :
    ]
    #CHANGE TEAM TO KART FOR THE RACE
    df_pilot_individual_karts = all_pilot_kart_records[category].\
        drop_duplicates(keep="first").copy().T.to_frame()
    df_pilot_individual_karts = df_pilot_individual_karts.reset_index(drop=False)
    #CHANGE TEAM TO KART FOR THE RACE
    for kart in range(len(df_pilot_individual_karts)):
        kart_with_pilot = all_pilot_kart_records.loc[
            #CHANGE TEAM TO KART FOR THE RACE
            df_from_recorded_records.loc[:, category] == df_pilot_individual_karts.loc[kart, category],
            :
        ]
        df_karts_and_pilots.loc[
            df_pilot_individual_karts.loc[kart, "index"],
            "temp_with_pilot"
        ] = kart_with_pilot.loc[:, "lap_time"].mean()
        df_karts_and_pilots.loc[
            df_pilot_individual_karts.loc[kart, "index"],
            "fastest_lap_with_pilot"
        ] = kart_with_pilot.loc[:, "lap_time"].min()
        
df_stats = pd.DataFrame.merge(
    df_karts_and_pilots,
    df_pilots,
    on="pilot"
)

df_stats = df_stats.reset_index(drop=True)
df_stats = df_stats.dropna()

# df_temp = pd.DataFrame(
#     {
#         "pilot": df_stats["pilot"].copy(),
#         "kart": df_stats["kart"].copy(),
#         "pilot_temp": df_stats.pop("pilot_temp"),
#         "temp_with_pilot": df_stats.pop("temp_with_pilot"),
#     }
# )

# df_fastet_lap = pd.DataFrame(
#     {
#         "pilot": df_stats.pop("pilot"),
#         "kart": df_stats.pop("kart"),
#         "pilot_fastest_lap": df_stats.pop("pilot_fastest_lap"),
#         "fastest_lap_with_pilot": df_stats.pop("fastest_lap_with_pilot"),
#     }
# )

list_of_names_to_delete = [
    "Карт 9",
    "Карт 6",
    "Карт 13",
    "Карт 21",
    "Карт 69",
    "Карт 18",
    "Карт 15",
    "Карт 8",
    "Карт 1",
    "Карт 10",
    "Карт 7",
    "Карт 4",
    "Карт 5",
    "Карт 3",
    "Карт 17",
    "Карт 14",
    "Карт 2",
    "Карт 12",
    "Карт 1",
]

for name in list_of_names_to_delete:
    needed_indexes = df_stats[
        (df_stats.loc[:,"pilot"] == name)
    ].index
    df_stats = df_stats.drop(needed_indexes)
needed_indexes = df_stats[
        (df_stats.loc[:,"kart"] == 0)
    ].index    
df_stats = df_stats.drop(needed_indexes)    

df_to_analyze = pd.DataFrame(
    {
        #"pilot": df_stats["pilot"].copy(),
        "kart": df_stats["kart"].copy(),
        "pilot_temp": df_stats.pop("pilot_temp"),
        "pilot_fastest_lap": df_stats.pop("pilot_fastest_lap"),
        "fastest_lap_with_pilot": df_stats.pop("fastest_lap_with_pilot"),
        "temp_with_pilot": df_stats.pop("temp_with_pilot"),
    }
)

df_to_analyze.to_csv("test.csv", index=False, index_label=False)

analyzer_functions.regression_process(df_to_analyze)

#print(df_fastet_lap.sort_values("pilot"))
    
end = time.perf_counter()

print(end-start)


