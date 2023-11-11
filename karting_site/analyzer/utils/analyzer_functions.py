import pandas as pd
import numpy as np
import requests

import time

import sys
from os.path import dirname, abspath
import importlib.util

from . import coeficient_creation_functions as coef_func
from recorder import models as recorder_models

def str_lap_time_into_float_change(
    lap_time: str
):
    try:
        lap_time = float(lap_time)
    except ValueError:
        split_lap_time = lap_time.split(":")
        lap_time = float(split_lap_time[0])*60+float(split_lap_time[1])
    return lap_time

def clear_df_from_unneeded_names(
    df_to_clear: pd.DataFrame
):
    list_of_names_to_delete = [
        "Карт 1","Карт 2","Карт 3","Карт 4",
        "Карт 5","Карт 6","Карт 7","Карт 8",
        "Карт 9","Карт 10","Карт 11","Карт 12",
        "Карт 13","Карт 14","Карт 15","Карт 16",
        "Карт 17","Карт 18","Карт 19","Карт 20",
        "Карт 21","Карт 22","Карт 33","Карт 44",
        "Карт 69","Карт 88",
    ]
    
    for name in list_of_names_to_delete:
        needed_indexes = df_to_clear[
            (df_to_clear.loc[:,"pilot"] == name)
        ].index
        df_to_clear = df_to_clear.drop(needed_indexes)
    
    return df_to_clear

def kart_column_into_str (kart):
    if kart > 9:
        kart = "kart_" + str(kart)
    else:
        kart = "kart_0" + str(kart)
    return kart
        

def records_columns_to_numeric (
    column_to_change: pd.Series
):
    try:
        column_to_change=pd.to_numeric(column_to_change)
    except ValueError:
        column_to_change.apply(str_lap_time_into_float_change)
        
    return column_to_change


def module_to_create_df_with_statistic(
    df_of_records: pd.DataFrame, 
    
    df_with_features: pd.DataFrame,
    column_to_look_for_feature: str,
    
    column_name_to_look_for_values_in: str,
    
    column_name_to_put_mean_value_in: str = None,
    column_name_to_put_min_value_in: str = None,
):
    df_with_features = df_with_features.copy()
    for feature in df_with_features.loc[:, column_to_look_for_feature].drop_duplicates():
        all_features_records = df_of_records.loc[
                df_of_records.loc[:, column_to_look_for_feature] == feature,
                :
        ]
        
        if column_name_to_put_mean_value_in != None:
            df_with_features.loc[
                df_with_features.loc[:, column_to_look_for_feature] == feature,
                column_name_to_put_mean_value_in
            ] = all_features_records.loc[:, column_name_to_look_for_values_in].mean()
        
        if column_name_to_put_min_value_in != None:
            df_with_features.loc[
                df_with_features.loc[:, column_to_look_for_feature] == feature,
                column_name_to_put_min_value_in
            ] = all_features_records.loc[:, column_name_to_look_for_values_in].min()
        
    return df_with_features


def module_to_create_pilot_statistics (
    df_of_records: pd.DataFrame,
):
    df_of_pilots = df_of_records.loc[
        (df_of_records.loc[:, "true_name" ]== True), 
        "pilot"
    ].drop_duplicates().copy().T.to_frame()
    df_of_pilots = df_of_pilots.reset_index(drop=True)
    
    df_of_pilots["pilot_temp"] = 0
    df_of_pilots["pilot_fastest_lap"] = 0
    
    df_of_pilots = module_to_create_df_with_statistic(
        df_of_records=df_of_records,
        
        df_with_features=df_of_pilots,
        column_to_look_for_feature="pilot",
        
        column_name_to_look_for_values_in="lap_time",
        column_name_to_put_mean_value_in="pilot_temp",
        column_name_to_put_min_value_in="pilot_fastest_lap",
    )
        
    return df_of_pilots


def module_to_create_kart_statistics (
    df_of_records: pd.DataFrame,
):
    df_of_karts = df_of_records.loc[
        df_of_records.loc[:, "true_kart" ]== True,
        "kart"
    ].drop_duplicates().T.to_frame()
    
    df_of_karts["kart_fastest_lap"] = 0
    
    df_of_karts = module_to_create_df_with_statistic(
        df_of_records=df_of_records,
        
        df_with_features=df_of_karts,
        column_to_look_for_feature="kart",
        
        column_name_to_look_for_values_in="lap_time",
        column_name_to_put_mean_value_in="kart_temp",
        column_name_to_put_min_value_in="kart_fastest_lap",
    )
    
    return df_of_karts


def module_to_create_karts_statistics_for_every_pilot(
    df_of_records: pd.DataFrame,
):
    df_pilot_on_karts = pd.DataFrame(
        {
            "pilot": pd.Series(dtype=str),
            "kart": pd.Series(dtype=str),
            "temp_with_pilot": pd.Series(dtype=float),
            "fastest_lap_with_pilot": pd.Series(dtype=float),   
        }
    )
    
    for pilot in df_of_records.loc[
        (df_of_records.loc[:, "true_name" ]== True),
        "pilot"
    ].drop_duplicates():
        all_pilot_kart_records = df_of_records.loc[
            df_of_records.loc[:, "pilot"]==pilot,
            :
        ]

        all_pilot_kart_records = all_pilot_kart_records.loc[
            (df_of_records.loc[:, "true_kart" ]== True),
            :
        ]

        all_pilot_kart_records.pop("true_name")
        all_pilot_kart_records.pop("true_kart")

        karts_of_pilot_df = module_to_create_df_with_statistic(
            df_of_records=all_pilot_kart_records,

            df_with_features=all_pilot_kart_records.drop_duplicates("kart"),
            column_to_look_for_feature="kart",

            column_name_to_look_for_values_in="lap_time",
            column_name_to_put_mean_value_in="temp_with_pilot",
            column_name_to_put_min_value_in="fastest_lap_with_pilot",
        )

        karts_of_pilot_df.pop("team")
        karts_of_pilot_df.pop("lap_time")
        karts_of_pilot_df.pop("s1")
        karts_of_pilot_df.pop("s2")


        df_pilot_on_karts = pd.concat(
            [df_pilot_on_karts, karts_of_pilot_df]   
        )
    return df_pilot_on_karts


def assemble_prediction (
    coeficient_for_prediction: float,
    df_of_pilots: pd.DataFrame,
    df_of_karts: pd.DataFrame,
):
    df_with_prediction = pd.DataFrame(
        {
            "kart": df_of_karts.loc[:, "kart"].drop_duplicates().copy(),
        }
    )
    
    max_temp = df_of_pilots["pilot_temp"].max()
    min_temp = df_of_pilots["pilot_temp"].min()
    temp_from_average_coeficient = (
                coeficient_for_prediction
            *
                (
                    max_temp
                -
                    min_temp
                )
            ) + min_temp
    
    df_with_prediction["temp_from_average_coeficient"] = temp_from_average_coeficient
    
    df_with_prediction = df_with_prediction.merge(
        df_of_karts,
        on="kart"
    )

    return df_with_prediction

def add_kart_column_into_return_dict(
    dict_to_process: dict,
    kart_column:pd.Series
):
    for prediction in range(len(dict_to_process["predictions"])):
            dict_to_process_df = pd.DataFrame(dict_to_process["predictions"][prediction])
            dict_to_process_df = dict_to_process_df.round(4)
            dict_to_process_df.insert(
                0,
                "kart",
                kart_column,
            )
            dict_to_process_df = dict_to_process_df.sort_values("kart", ignore_index=True, inplace=False)
            dict_to_process["predictions"][prediction] = dict_to_process_df.to_dict(
                    orient="records",
                    #indent=2
                )
    return dict_to_process

def collect_race_records_into_DataFrame (
    race_id
):
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
    
    return df_from_recorded_records

def does_race_has_true_karts(
    df_with_race_records
):
    true_kart_count = df_with_race_records["true_kart"].value_counts()
    try:
        true_kart_count = true_kart_count[True]
        return True
    except KeyError:
        return False

def clear_outstanding_laps (
    df_with_race_records: pd.DataFrame,
    margin_to_add_to_mean_time: int = 5,
):
    mean_lap_time = df_with_race_records.loc[:, "lap_time"].mean()
    df_with_race_records["lap_time"] = df_with_race_records.loc[
        df_with_race_records.loc[:, "lap_time"] < mean_lap_time+margin_to_add_to_mean_time, 
        "lap_time"
    ]
    del mean_lap_time, margin_to_add_to_mean_time
    
    return df_with_race_records

def create_df_from_recorded_records(
    race_id
):    
    df_from_recorded_records = collect_race_records_into_DataFrame(
        race_id=race_id
    )
    
    if not does_race_has_true_karts(
        df_with_race_records=df_from_recorded_records
    ): 
        df_from_recorded_records["kart"] = df_from_recorded_records["team"].astype(int)
        df_from_recorded_records["true_kart"] = True
    

    df_from_recorded_records["kart"] = df_from_recorded_records["kart"].apply(
        kart_column_into_str
    )
    df_from_recorded_records["pilot"] = df_from_recorded_records["pilot"].str.strip()

    columns_to_change=[
            "lap_time",
            "s1",
            "s2",
        ]
    for column in columns_to_change:    
        df_from_recorded_records[column]=records_columns_to_numeric(
            column_to_change=df_from_recorded_records[column]
        )
    del columns_to_change

    df_from_recorded_records = clear_outstanding_laps(
        df_with_race_records=df_from_recorded_records
    )

    #df_from_recorded_records.pop("segment")
    df_from_recorded_records.pop("lap")

    return df_from_recorded_records

def create_df_stats(
    df_pilot_on_karts: pd.DataFrame,
    df_pilots: pd.DataFrame,
    df_karts: pd.DataFrame
):
    df_stats = pd.DataFrame.merge(
        df_pilot_on_karts,
        df_pilots,
        on="pilot"
    )

    df_stats = pd.DataFrame.merge(
        df_stats,
        df_karts,
        on="kart"
    )

    df_stats = df_stats.reset_index(drop=True)
    df_stats = df_stats.dropna()   
    
    return df_stats

def form_return_for__analyze_race__after_error_check (
    dict_with_predictions:dict,
    
    series_of_karts:pd.Series,
    word_to_name_predictions_type:str,
):
    return_dict = {}
    try:
        dict_with_predictions["error"]
    except KeyError: 
        return_dict.update(
            {
                f"{word_to_name_predictions_type}_r2_scores" : dict_with_predictions["r2_score_values_dict"]
            }
        )

        dict_with_predictions = add_kart_column_into_return_dict(
            dict_to_process=dict_with_predictions,
            kart_column=series_of_karts 
        )

        return_dict.update(
            {
                f"{word_to_name_predictions_type}_predictions": dict_with_predictions["predictions"]
            }
        )
    else:
        return_dict.update(
            {
                f"{word_to_name_predictions_type}_message": dict_with_predictions["message"]
            }
        )

    return return_dict