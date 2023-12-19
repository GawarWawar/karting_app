# FORMING DATABASE TO ANALIZE
import numpy as np
import pandas as pd
from dateutil import parser

import time
import logging

import sys
import os

from recorder import models as recorder_models
from . import models

from .utils.analyzation_process import laps_frame_creation
from .utils.analyzation_process import statistic_creation
from .utils.analyzation_process import coeficient_creation_functions as coef_func
from .utils.analyzation_process import laps_frame_modifications
from .utils.analyzation_process import functions_for_return

from .utils.prediction_process import regression_process
from .utils.prediction_process import prediction_processing
from .utils.prediction_process import regression_models

import warnings
# Suppress FutureWarning messages
warnings.simplefilter(action='ignore', category=FutureWarning)

def compute_kart_statistic(race_id):

    start = time.perf_counter()
    
    df_from_recorded_records = laps_frame_creation.create_df_from_recorded_records(
        race_id=race_id
    )
    
    df_from_recorded_records = laps_frame_modifications.clear_column_from_unneeded_strings(
        df_from_recorded_records,
        
        column_to_look_into="pilot_name",
        wrong_string_to_look_for="Карт ",
    )
    df_from_recorded_records = df_from_recorded_records[df_from_recorded_records["true_kart"]]
    df_from_recorded_records = df_from_recorded_records[df_from_recorded_records["true_name"]]
    
    df_from_recorded_records = laps_frame_modifications.clear_outstanding_laps(
        df_with_race_records=df_from_recorded_records
    )

    # df_from_recorded_records.pop("team_segment")
    df_from_recorded_records.pop("lap_count")

    df_pilots = statistic_creation.create_pilot_statistics(
        df_with_records=df_from_recorded_records,
    )
   
    df_pilots = df_pilots.dropna()
    df_pilots = df_pilots.reset_index(drop=True)

    
    df_coeficient = coef_func.create_primary_coeficient()

    df_pilots = coef_func.add_coeficients_and_temp_from_average_coeficient_to_df(
        df_to_create_coeficients_into=df_pilots,
        df_of_primary_coeficient=df_coeficient
    )
    del df_coeficient

    df_karts = statistic_creation.create_kart_statistics(
        df_with_records=df_from_recorded_records,
    )

    df_pilot_on_karts = statistic_creation.module_to_create_karts_statistics_for_every_pilot(
        df_of_records=df_from_recorded_records,
    )
   
    df_stats = statistic_creation.create_df_stats(
        df_pilot_on_karts=df_pilot_on_karts,
        df_pilots=df_pilots,
        df_karts=df_karts,
    )
    
    
    return_dict = {
        "data": {}
    }
    
    df_stats = df_stats.sort_values(["kart", "team_segment"], inplace=False)
    
    for kart in df_stats.loc[:, "kart"].drop_duplicates():
        kart_dict = {
            "kart": kart, 
        }
        pilots_of_kart_index = df_stats.loc[
            df_stats.loc[:, "kart"] == kart,
            "pilot_name"
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
                        "pilot_name": df_stats.loc[index, "pilot_name"],
                        "temp_with_pilot" : df_stats.loc[index, "temp_with_pilot"],
                        "fastest_lap_with_pilot" : df_stats.loc[index, "fastest_lap_with_pilot"],
                        "pilot_temp" : df_stats.loc[index, "pilot_temp"],
                        "pilot_fastest_lap" : df_stats.loc[index, "pilot_fastest_lap"],
                        "team_segment": df_stats.loc[index, "team_segment"],
                        #"this_race_coeficient" : df_stats.loc[index, "this_race_coeficient"],
                        #"pilot_coeficient" : df_stats.loc[index, "coeficient"],
                        #"average_coeficient" : df_stats.loc[index, "average_coeficient"],
                        "temp_from_average_coeficient" : df_stats.loc[index, "temp_from_average_coeficient"],
                    }
            )
        return_dict["data"].update(
            {
                "karts": kart_dict
            }
        )
    
    end = time.perf_counter()
    print(end-start)
    return return_dict
    

def analyze_race(
    race_id: int,
    
    coeficients_for_predictions: list[float] = [0.0],
    
    logg_level: str|None = "WARNING",
    
    how_many_digits_after_period_to_leave_in: int = 4,
    
    margin_in_seconds_to_add_to_mean_time: int = 5,
    
    regression_model_builders = [
        regression_models.MultipleLinearRegression_,
        regression_models.PolinomialRegression_,
        regression_models.SupportVectorRegression_,
        regression_models.DecisionTreeRegression_,
        regression_models.RandomForestRegression_,
    ],
    minimum_value_to_r2 = 0,
    size_of_test_set = 0.15,
    train_test_split_random_state = 2,
    sequence_number_of_columns_to_OHE = [0]
):  
    if logg_level is not None:
        logger_set_up_start_timer = time.perf_counter()
        
        
        # Create logger to make logs
        logger_name_and_file_name = f"race_id_{race_id}"
        race_logger = logging.getLogger(logger_name_and_file_name)
        race_logger.setLevel(logg_level)
                
        
        # FileHandler change for logger, to change logger location
        file_handler = logging.FileHandler(
            f'analyzer/data/logs/{logger_name_and_file_name}.log'
        )
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        race_logger.addHandler(file_handler)
        
        logger_set_up_end_time = time.perf_counter()
        
        race_logger.debug(f"{logger_set_up_end_time-logger_set_up_start_timer} secons took logger to set up")
        race_logger.debug("START")
        
        start_timer = time.perf_counter()
    
    df_from_recorded_records = laps_frame_creation.create_df_from_recorded_records(
        race_id=race_id
    )
    
    df_from_recorded_records = laps_frame_modifications.clear_column_from_unneeded_strings(
        df_from_recorded_records,
        
        column_to_look_into="pilot_name",
        wrong_string_to_look_for="Карт ",
    )
    df_from_recorded_records = df_from_recorded_records[df_from_recorded_records["true_kart"]]
    df_from_recorded_records = df_from_recorded_records[df_from_recorded_records["true_name"]]
    
    df_from_recorded_records = laps_frame_modifications.clear_outstanding_laps(
        df_with_race_records = df_from_recorded_records,
        
        margin_to_add_to_mean_time=margin_in_seconds_to_add_to_mean_time
    )

    df_from_recorded_records.pop("team_segment")
    df_from_recorded_records.pop("lap_count")

    df_pilots = statistic_creation.create_pilot_statistics(
        df_with_records=df_from_recorded_records,
    )
   
    df_pilots = df_pilots.dropna()
    df_pilots = df_pilots.reset_index(drop=True)

    
    df_coeficient = coef_func.create_primary_coeficient(
        how_many_digits_after_period_to_leave_in = how_many_digits_after_period_to_leave_in,
        logger_instance=race_logger
    )

    df_pilots = coef_func.add_coeficients_and_temp_from_average_coeficient_to_df(
        df_to_create_coeficients_into=df_pilots,
        df_of_primary_coeficient=df_coeficient,
        
        how_many_digits_after_period_to_leave_in = how_many_digits_after_period_to_leave_in,
        logger_instance=race_logger
    )
    del df_coeficient

    df_karts = statistic_creation.create_kart_statistics(
        df_with_records=df_from_recorded_records,
    )

    df_pilot_on_karts = statistic_creation.module_to_create_karts_statistics_for_every_pilot(
        df_of_records=df_from_recorded_records,
    )
   
    df_stats = statistic_creation.create_df_stats(
        df_pilot_on_karts=df_pilot_on_karts,
        df_pilots=df_pilots,
        df_karts=df_karts,
    )
    
    list_with_predictions = []
    for coeficient in coeficients_for_predictions:
        df_with_prediction = prediction_processing.assemble_prediction(
            coeficient,
            df_of_pilots=df_pilots.copy(),
            df_of_karts=df_karts.copy(),
        )
        list_with_predictions.append(
            df_with_prediction
        )

    try:
        df_to_analyze = pd.DataFrame(
            {
                #"pilot_name": df_stats["pilot_name"].copy(),
                "kart": df_stats["kart"].copy(),
                #"pilot_temp": df_stats.pop("pilot_temp"),
                #"pilot_fastest_lap": df_stats.pop("pilot_fastest_lap"),
                #"this_race_coeficient": df_stats.pop("this_race_coeficient"),
                #"pilot_coeficient": df_stats.pop("coeficient"),
                #"average_coeficient": df_stats.pop("average_coeficient"),
                "temp_from_average_coeficient": df_stats.pop("temp_from_average_coeficient"),
                "kart_temp": df_stats.pop("kart_temp"),
                "kart_fastest_lap": df_stats.pop("kart_fastest_lap"),
                
                "temp_with_pilot": df_stats.pop("temp_with_pilot"),
            }
        )
    except KeyError:
        return None


    return_dict = {
        "data": {    
            #"temp_predictions": [],
            #"temp_r2_scores": {},
            #"fastestlap_predictions": [],
            #"fastestlap_r2_scores": {},
        }
    } 

    series_of_karts = pd.Series(
        df_with_prediction.loc[:, "kart"].drop_duplicates().copy(),
        name="kart",
    )

    if logg_level is not None:
        race_logger.debug("1. Temp")
    dicts_from_temp_predictions = regression_process.regression_process(
        df_to_analyze, list_with_predictions,
        
        logger_instance=race_logger,
        
        regression_model_builders=regression_model_builders,
        minimum_value_to_r2=minimum_value_to_r2,
        size_of_test_set=size_of_test_set,
        train_test_split_random_state=train_test_split_random_state,
        sequence_number_of_columns_to_OHE=sequence_number_of_columns_to_OHE,
        
        how_many_digits_after_period_to_leave_in = how_many_digits_after_period_to_leave_in
    ) 
    data = functions_for_return.form_return_after_analyzation_with_error_check(
        dict_with_predictions=dicts_from_temp_predictions,
        series_of_karts=series_of_karts,
        word_to_name_predictions_type="temp",
    )
    return_dict["data"].update(data)

    df_to_analyze.pop("temp_with_pilot")
    df_to_analyze["fastest_lap_with_pilot"]=df_stats.pop("fastest_lap_with_pilot")
    del df_stats

    if logg_level is not None:
        race_logger.debug("2. Fastest lap")
    dicts_from_fastestlap_predictions = regression_process.regression_process(
        df_to_analyze, list_with_predictions,
        
        logger_instance=race_logger,
        
        regression_model_builders=regression_model_builders,
        minimum_value_to_r2=minimum_value_to_r2,
        size_of_test_set=size_of_test_set,
        train_test_split_random_state=train_test_split_random_state,
        sequence_number_of_columns_to_OHE=sequence_number_of_columns_to_OHE,
        
        how_many_digits_after_period_to_leave_in = how_many_digits_after_period_to_leave_in
    )
    data = functions_for_return.form_return_after_analyzation_with_error_check(
        dict_with_predictions=dicts_from_fastestlap_predictions,
        series_of_karts=series_of_karts,
        word_to_name_predictions_type="fastestlap",
    )
    return_dict["data"].update(data)
    
    if logg_level is not None:
        end_timer = time.perf_counter()
        race_logger.info(f"END:{end_timer-start_timer} seconds were used by whole analyzation process before finishing")
        race_logger.removeHandler(file_handler)
        

    return return_dict

