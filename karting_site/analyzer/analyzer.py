# FORMING DATABASE TO ANALIZE
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from dateutil import parser

import time
import pprint
import sys
import os

from recorder import models as recorder_models
from . import pilot_rating
from . import models

from .utils import analyzer_functions
from .utils import regression_process
from .utils import coeficient_creation_functions as coef_func

def analyze_race(race_id):

    start = time.perf_counter()

    competition = True

    if competition:
        category = "kart"
    else:
        category = "team"
    
    df_from_recorded_records = pd.DataFrame(
        {
            "team": pd.Series(int),
            "pilot": pd.Series(str),
            "kart": pd.Series(int),
            "lap": pd.Series(int),
            "lap_time": pd.Series(float),
            "s1": pd.Series(float),
            "s2": pd.Series(float),
            "segment": pd.Series(int),
            "true_name": pd.Series(bool),
            "true_kart": pd.Series(bool)
        }
    )
    df_from_recorded_records = df_from_recorded_records.drop(0)

    race = recorder_models.Race.objects.get(pk = race_id)
    race_records = recorder_models.RaceRecords.objects.filter(race = race).values_list()
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
    
    df_from_recorded_records.pop("id")
    df_from_recorded_records.pop("race")

    df_from_recorded_records["kart"] = "kart_" + df_from_recorded_records["kart"].astype(str)
    df_from_recorded_records["pilot"] = df_from_recorded_records["pilot"].str.strip()

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

    # df_coeficient = pd.read_csv(
    #     "data/pilot_rating.csv",
    #     dtype={
    #         "pilot": str,
    #         "coeficient": float
    #     }
    # )
    
    df_coeficient = pilot_rating.create_pilot_rating()

    df_pilots = coef_func.add_coeficients_and_temp_from_average_coeficient_to_df(
        df_to_create_coeficients_into=df_pilots,
        df_of_primary_coeficient=df_coeficient
    )

    del df_coeficient

    # CHANGE INTO RETURNING TO THE PAGE, WHEN POSTING WILL BE READY    
    #print(df_pilots.sort_values("pilot_temp", ignore_index=True, inplace=False))

    df_karts = analyzer_functions.module_to_create_kart_statistics(
        df_of_records=df_from_recorded_records,
        category=category
    )

    df_with_prediction = analyzer_functions.assemble_prediction(
        0.0,
        df_of_pilots=df_pilots.copy(),
        df_of_karts=df_karts.copy(),
    )

    # Deleting from df_pilots info, that won`t be used in regression process
    # df_pilots.pop("pilot_temp")
    # df_pilots.pop("this_race_coeficient")
    # df_pilots.pop("pilot_coeficient")
    # df_pilots.pop("average_coeficient")
    # df_pilots.pop("pilot_fastest_lap")


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
        df_karts.copy(),
        on=category
    )

    df_stats = df_stats.reset_index(drop=True)
    df_stats = df_stats.dropna()   

    try:
        df_to_analyze = pd.DataFrame(
            {
                #"pilot": df_stats["pilot"].copy(),
                "kart": df_stats["kart"].copy(),
                #"pilot_temp": df_stats.pop("pilot_temp"),
                #"pilot_fastest_lap": df_stats.pop("pilot_fastest_lap"),
                #"this_race_coeficient": df_stats.pop("this_race_coeficient"),
                #"pilot_coeficient": df_stats.pop("pilot_coeficient"),
                #"average_coeficient": df_stats.pop("average_coeficient"),
                "temp_from_average_coeficient": df_stats.pop("temp_from_average_coeficient"),
                "kart_fastest_lap": df_stats.pop("kart_fastest_lap"),
                "kart_temp": df_stats.pop("kart_temp"),
                "temp_with_pilot": df_stats.pop("temp_with_pilot"),
            }
        )
    except KeyError:
        return None


    return_dict = {
        "temp_predictions": [],
        "temp_r2_scores": {},
        "fastestlap_predictions": [],
        "fastestlap_r2_scores": {},
    } 

    print("1.")
    dicts_from_temp_predictions = regression_process.regression_process(df_to_analyze, [df_with_prediction]) 
    if dicts_from_temp_predictions is None:
        return None

    return_dict["temp_r2_scores"] = dicts_from_temp_predictions["r2_score_values_dict"]

    df_to_analyze.pop("temp_with_pilot")
    df_to_analyze["fastest_lap_with_pilot"]=df_stats.pop("fastest_lap_with_pilot")
    del df_stats

    print("2.")
    dicts_from_fastestlap_predictions = regression_process.regression_process(df_to_analyze, [df_with_prediction])

    return_dict["fastestlap_r2_scores"] = dicts_from_fastestlap_predictions["r2_score_values_dict"]

    series_of_karts = pd.Series(
        df_with_prediction.loc[:, "kart"].drop_duplicates().copy(),
        name="kart",
    )
    for i in range(len(dicts_from_temp_predictions["predictions"])):
        temp_prediction_df = pd.DataFrame(dicts_from_temp_predictions["predictions"][i])
        temp_prediction_df = temp_prediction_df.round(4)
        temp_prediction_df.insert(
            0,
            "kart",
            series_of_karts,
        )
        dicts_from_temp_predictions["predictions"][i] = temp_prediction_df.to_dict(
                orient="records",
                #indent=2
            )
        
        fastestlap_prediction_df = pd.DataFrame(dicts_from_fastestlap_predictions["predictions"][i])
        fastestlap_prediction_df = fastestlap_prediction_df.round(4)
        fastestlap_prediction_df.insert(
            0,
            "kart",
            series_of_karts,
        )
        dicts_from_fastestlap_predictions["predictions"][i] = fastestlap_prediction_df.to_dict(
                orient="records",
                #indent=2
            )
        
    return_dict["temp_predictions"] = dicts_from_temp_predictions["predictions"]
    return_dict["fastestlap_predictions"] = dicts_from_fastestlap_predictions["predictions"]
        
    end = time.perf_counter()

    print(end-start)

    return return_dict

