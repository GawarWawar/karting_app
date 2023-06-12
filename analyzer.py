# FORMING DATABASE TO ANALIZE
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from dateutil import parser

import time

import sys
import os

from utils import analyzer_functions
from utils import regression_process
from utils import coeficient_creation_functions as coef_func

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

df_from_recorded_records["kart"] = "kart_" + df_from_recorded_records["kart"].astype(str)

df_from_recorded_records = analyzer_functions.records_columns_to_numeric(
    df_from_recorded_records,
    columns_to_change=[
        "lap_time",
        "s1",
        "s2",
    ]
)

mean_lap_time = df_from_recorded_records.loc[:, "lap_time"].mean()
margin_to_add_to_mean_time = 5
df_from_recorded_records["lap_time"] = df_from_recorded_records.loc[
    df_from_recorded_records.loc[:, "lap_time"] < mean_lap_time+margin_to_add_to_mean_time, 
    "lap_time"
]
del mean_lap_time, margin_to_add_to_mean_time

df_from_recorded_records.pop("segment")
df_from_recorded_records.pop("lap")

df_pilots = analyzer_functions.module_to_create_pilot_statistics(
    df_of_records=df_from_recorded_records
)
df_pilots = analyzer_functions.clear_df_from_unneeded_names(
    df_pilots
)
df_pilots = df_pilots.dropna()
df_pilots = df_pilots.reset_index(drop=True)

df_coeficient = pd.read_csv(
    "data/pilot_rating.csv",
    dtype={
        "pilot": str,
        "coeficient": float
    }
)
df_pilots["temp_coeficient"] = coef_func.column_with_lap_time_to_coeficient(
                df_pilots.loc[:,"pilot_temp"].copy()
            )


df_karts = analyzer_functions.module_to_create_kart_statistics(
    df_of_records=df_from_recorded_records,
    category=category
)

df_pilot_on_karts = analyzer_functions.module_to_create_karts_statistics_for_every_pilot(
    df_of_records=df_from_recorded_records,
    category=category
)

df_stats = pd.DataFrame.merge(
    df_pilot_on_karts,
    df_pilots,
    on="pilot"
)

df_stats = pd.DataFrame.merge(
    df_stats,
    df_karts,
    on=category
)

df_stats = df_stats.reset_index(drop=True)
df_stats = df_stats.dropna()   

df_to_analyze = pd.DataFrame(
    {
        #"pilot": df_stats["pilot"].copy(),
        "kart": df_stats["kart"].copy(),
        "pilot_temp": df_stats.pop("pilot_temp"),
        "pilot_fastest_lap": df_stats.pop("pilot_fastest_lap"),
        "temp_coeficient": df_stats.pop("temp_coeficient"),
        "kart_fastest_lap": df_stats.pop("kart_fastest_lap"),
        "kart_temp": df_stats.pop("kart_temp"),
        "temp_with_pilot": df_stats.pop("temp_with_pilot"),
    }
)

df_to_analyze.to_csv("test.csv", index=False, index_label=False)

df_with_prediction = analyzer_functions.assemble_prediction(
    "Ревчук Олексій",
    df_of_pilots=df_pilots.copy(),
    df_of_karts=df_karts.copy(),
)
df_with_prediction.pop("pilot")

df_with_prediction_2 = analyzer_functions.assemble_prediction(
    "Ревчук Олександр",
    df_of_pilots=df_pilots.copy(),
    df_of_karts=df_karts.copy(),
)
df_with_prediction_2.pop("pilot")

print("1.")
list_of_dicts_with_predictions = regression_process.regression_process(df_to_analyze, [df_with_prediction, df_with_prediction_2])

# for i in range(len(list_of_dicts_with_predictions)):
#     prediction_df = pd.DataFrame(list_of_dicts_with_predictions[i])
#     prediction_df = prediction_df.round(4)
#     prediction_df.to_csv(f"predictions{i}.csv", index=False, index_label=False )

df_to_analyze.pop("temp_with_pilot")
df_to_analyze["fastest_lap_with_pilot"]=df_stats.pop("fastest_lap_with_pilot")
del df_stats

print("2.")
regression_process.regression_process(df_to_analyze, [df_with_prediction])
    
end = time.perf_counter()

print(end-start)


