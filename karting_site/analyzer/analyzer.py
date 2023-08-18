# FORMING DATABASE TO ANALIZE
import numpy as np
import pandas as pd
from dateutil import parser

import time
import pprint
import sys
import os

from recorder import models as recorder_models
from .utils import pilot_rating
from . import models

from .utils import analyzer_functions
from .utils import regression_process
from .utils import coeficient_creation_functions as coef_func

def compute_kart_statistic(race_id):

    start = time.perf_counter()
    
    df_from_recorded_records = analyzer_functions.create_df_from_recorded_records(
        race_id=race_id
    )
    
    df_pilots = analyzer_functions.module_to_create_pilot_statistics(
        df_of_records=df_from_recorded_records
    )
    df_pilots = analyzer_functions.clear_df_from_unneeded_names(
        df_pilots
    )
    df_pilots = df_pilots.dropna()
    df_pilots = df_pilots.reset_index(drop=True)

    
    df_coeficient = pilot_rating.create_pilot_rating()

    df_pilots = coef_func.add_coeficients_and_temp_from_average_coeficient_to_df(
        df_to_create_coeficients_into=df_pilots,
        df_of_primary_coeficient=df_coeficient
    )

    del df_coeficient

    df_karts = analyzer_functions.module_to_create_kart_statistics(
        df_of_records=df_from_recorded_records,
    )

    df_pilot_on_karts = analyzer_functions.module_to_create_karts_statistics_for_every_pilot(
        df_of_records=df_from_recorded_records,
    )

    df_stats = analyzer_functions.create_df_stats(
        df_pilot_on_karts=df_pilot_on_karts,
        df_pilots=df_pilots,
        df_karts=df_karts,
    )
    return_dict = {
        "data": []
    }
    
    df_stats = df_stats.sort_values(["kart", "segment"], inplace=False)
    
    for kart in df_stats.loc[:, "kart"].drop_duplicates():
        kart_dict = {
            "kart": kart, 
        }
        pilots_of_kart_index = df_stats.loc[
            df_stats.loc[:, "kart"] == kart,
            "pilot"
        ].index
        kart_dict.update(
            {
                "kart_fastest_lap": df_stats.loc[pilots_of_kart_index[0], "kart_fastest_lap"],
                "kart_temp": df_stats.loc[pilots_of_kart_index[0], "kart_temp"],
                "pilots": []
            }
        )
        for index in pilots_of_kart_index:
            kart_dict["pilots"].append(
                    {
                        "pilot": df_stats.loc[index, "pilot"],
                        "temp_with_pilot" : df_stats.loc[index, "temp_with_pilot"],
                        "fastest_lap_with_pilot" : df_stats.loc[index, "fastest_lap_with_pilot"],
                        "pilot_temp" : df_stats.loc[index, "pilot_temp"],
                        "pilot_fastest_lap" : df_stats.loc[index, "pilot_fastest_lap"],
                        "team_segment": df_stats.loc[index, "segment"],
                        #"this_race_coeficient" : df_stats.loc[index, "this_race_coeficient"],
                        #"pilot_coeficient" : df_stats.loc[index, "pilot_coeficient"],
                        #"average_coeficient" : df_stats.loc[index, "average_coeficient"],
                        "temp_from_average_coeficient" : df_stats.loc[index, "temp_from_average_coeficient"],
                    }
            )
        return_dict["data"].append(kart_dict)
    
    end = time.perf_counter()
    print(end-start)
    return return_dict
    

def analyze_race(race_id):

    start = time.perf_counter()
    
    df_from_recorded_records = df_from_recorded_records = analyzer_functions.create_df_from_recorded_records(
        race_id=race_id
    )

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
    )

    df_stats = analyzer_functions.create_df_stats(
        df_pilot_on_karts=df_pilot_on_karts,
        df_pilots=df_pilots,
        df_karts=df_karts,
    )

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
        #"temp_predictions": [],
        #"temp_r2_scores": {},
        #"fastestlap_predictions": [],
        #"fastestlap_r2_scores": {},
    } 

    series_of_karts = pd.Series(
        df_with_prediction.loc[:, "kart"].drop_duplicates().copy(),
        name="kart",
    )

    print("1.")
    dicts_from_temp_predictions = regression_process.regression_process(df_to_analyze, [df_with_prediction]) 
    return_dict = analyzer_functions.form_return_for__analyze_race__after_error_check(
        dict_with_predictions=dicts_from_temp_predictions,
        series_of_karts=series_of_karts,
        word_to_name_predictions_type="temp",
        return_dict=return_dict
    )

    df_to_analyze.pop("temp_with_pilot")
    df_to_analyze["fastest_lap_with_pilot"]=df_stats.pop("fastest_lap_with_pilot")
    del df_stats

    print("2.")
    dicts_from_fastestlap_predictions = regression_process.regression_process(df_to_analyze, [df_with_prediction])
    return_dict = analyzer_functions.form_return_for__analyze_race__after_error_check(
        dict_with_predictions=dicts_from_fastestlap_predictions,
        series_of_karts=series_of_karts,
        word_to_name_predictions_type="fastestlap",
        return_dict=return_dict
    )
    
    end = time.perf_counter()
    print(end-start)

    return return_dict

