# FORMING DATABASE TO ANALIZE
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

import sys
import os

import pprint

df_from_recorded_records = pd.read_csv("pilots_stats_template.csv")

path_to_records = "data/records"
files_to_read = os.listdir(path_to_records)
for file in files_to_read:
    try:
        df_to_concate = pd.read_csv(path_to_records+"/"+file)
        df_from_recorded_records = pd.concat([df_from_recorded_records, df_to_concate], ignore_index=True)
    except pd.errors.EmptyDataError:
        pass


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
    ["pilot","team"] #CHANGE TEAM TO KART FOR THE RACE
].drop_duplicates(keep="first").copy()

df_pilots["temp"] = 0
for pilot in df_pilots.loc[:, "pilot"]:
    all_pilot_records = df_from_recorded_records.loc[
            df_from_recorded_records.loc[:, "pilot"] == pilot,
            :
        ]
    
    df_pilots.loc[
        df_pilots.loc[:, "pilot"] == pilot,
        "temp"
    ] = all_pilot_records.loc[:, "lap_time"].mean()

df_karts_and_pilots["temp_with_pilot"] = 0
df_karts_and_pilots["fastest_lap_with_pilot"] = 0

for pilot in df_karts_and_pilots.loc[:, "pilot"]:
    all_pilot_kart_records = df_from_recorded_records.loc[
        df_from_recorded_records.loc[:, "pilot"]==pilot,
        :
    ]
    #CHANGE TEAM TO KART FOR THE RACE
    df_pilot_individual_karts = all_pilot_kart_records["team"].\
        drop_duplicates(keep="first").copy().T.to_frame()
    df_pilot_individual_karts = df_pilot_individual_karts.reset_index(drop=False)
    #CHANGE TEAM TO KART FOR THE RACE
    for kart in range(len(df_pilot_individual_karts)):
        kart_with_pilot = all_pilot_kart_records.loc[
            #CHANGE TEAM TO KART FOR THE RACE
            df_from_recorded_records.loc[:, "team"] == df_pilot_individual_karts.loc[kart, "team"],
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
    df_pilots,
    df_karts_and_pilots,
    on="pilot"
)
print(df_stats.sort_values("pilot"))

df_from_recorded_records.to_csv("test.csv", index=False, index_label=False)

    
