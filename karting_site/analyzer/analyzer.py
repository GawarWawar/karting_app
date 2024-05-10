# FORMING DATABASE TO ANALIZE
from dateutil import parser
import logging
import numpy as np
import pandas as pd

import sys
import os

import time

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

from .utils import logging_initialization

import warnings
# Suppress FutureWarning messages
warnings.simplefilter(action='ignore', category=FutureWarning)

def compute_kart_statistic(
    race_id,
    
    logg_level: str|None = "WARNING",
    how_many_digits_after_period_to_leave_in: int = 4,
    margin_in_seconds_to_add_to_mean_time: int = 5,
):
    """
    Compute statistics for each kart in a race and return the results in a structured format.

    Parameters:
    - race_id: Identifier for the race.
    - logg_level (str|None, optional): Logging level for the race logger. Default set to "WARNING" level.
    - how_many_digits_after_period_to_leave_in (int, optional): Number of digits to round floating-point values to. Default set to 4 digits.
    - margin_in_seconds_to_add_to_mean_time (int, optional): Margin in seconds to add to the mean lap time. Default set to 5 seconds.

    Returns:
    - dict: A dictionary containing computed statistics for each kart in the race.
    
    Note:
    This function performs the following steps:
    1. Loads race records and creates a DataFrame.
    2. Cleans and filters the DataFrame, removing irrelevant data.
    3. Computes pilot and kart statistics based on the cleaned DataFrame.
    4. Creates a structured dictionary containing detailed statistics for each kart.
    
    The function utilizes a logging system to record the process details if a logging level is specified.
    
    The generated statistics include information about each kart, its fastest lap, tempo, and associated pilots.
    """
    # Set up the logger for the race
    if logg_level is not None:
        logger_set_up_start_timer = time.perf_counter()
        
        # Create logger to make logs
        race_logger = logging_initialization.get_or_create_logger_for_race(
            race_id = race_id,
            log_level = logg_level
        )
                
        # FileHandler change for logger, to change logger location
        file_handler = logging_initialization.create_and_assign_filehandler_to_logger(
            race_logger = race_logger,
            race_id=race_id
        )
        
        logger_set_up_end_time = time.perf_counter()
        
        race_logger.debug(f"{logger_set_up_end_time-logger_set_up_start_timer} secons took logger to set up")
        race_logger.debug("START")
        
        start_timer = time.perf_counter()
    
    
    # 1. Loads race records and creates a DataFrame.
    try:
        df_from_recorded_records = laps_frame_creation.create_df_from_recorded_records(
            race_id=race_id
        )
    except ValueError:
        return {
            "data":{},
            "race_id": race_id
        }

    
    # 2. Cleans and filters the DataFrame, removing irrelevant data.
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

    # df_from_recorded_records.pop("team_segment")
    df_from_recorded_records.pop("lap_count")

    # 3. Computes pilot and kart statistics based on the cleaned DataFrame.
    df_pilots = statistic_creation.create_pilot_statistics(
        df_with_records=df_from_recorded_records,
    )

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
   
    df_stats = statistic_creation.merge_all_statistic_about_pilots_and_karts(
        df_with_each_kart_and_pilot_combo_statistic = df_pilot_on_karts,
        df_with_statistic_of_pilots = df_pilots,
        df_with_statistic_of_karts = df_karts,
    )
    
    # 4. Creates a structured dictionary containing detailed statistics for each kart.
    return_dict = {
        "data": {
            "karts":[]
        }
    }
    
    df_stats = df_stats.sort_values(["kart", "team_segment"], inplace=False)
        
    kart_grouped = df_stats.groupby("kart")
    del df_stats

    # Iterate through each kart and extract statistics
    for kart, group in kart_grouped:
        kart_dict = {
            "kart": kart,
            "kart_fastest_lap": group.iloc[0]["kart_fastest_lap"],
            "kart_temp": group.iloc[0]["kart_temp"],
            "pilots": group[
                [
                    "pilot_name", 
                    "temp_with_pilot", 
                    "fastest_lap_with_pilot", 
                    "pilot_temp", 
                    "pilot_fastest_lap", 
                    "team_segment", 
                    #"this_race_coeficient",
                    #"pilot_coeficient",
                    #"average_coeficient",
                    "temp_from_average_coeficient"
                ]
            ].to_dict(orient="records")
        }
        
        return_dict["data"]["karts"].append(kart_dict)

    # Add race_id to the return dictionary
    return_dict.update(
        {
            "race_id": race_id
        }
    )
    
    # Log the time taken by the function if logging is enabled
    if logg_level is not None:
        end_timer = time.perf_counter()
        race_logger.info(f"END:{end_timer-start_timer} seconds were used by generating statistic process before finishing")
        race_logger.removeHandler(file_handler)
        
    return return_dict
    

def analyze_race(
    race_id: int,
    
    coeficients_for_predictions: list[float] = [0.0],
    
    logg_level: str|None = "WARNING",
    
    how_many_digits_after_period_to_leave_in: int = 4,
    
    margin_in_seconds_to_add_to_mean_time: int = 5,
    
    regression_models_instances = [
        regression_models.MultipleLinearRegression_,
        # regression_models.PolinomialRegression_,
        regression_models.SupportVectorRegression_,
        # regression_models.DecisionTreeRegression_,
        regression_models.RandomForestRegression_,
    ],
    minimum_value_to_r2:float = 0.0,
    size_of_test_set:float = 0.15,
    set_n_splits: int = 20,
    train_test_split_random_state = 2,
):  
    """
    Analyze a kart race by generating statistics and making tempo and fastest lap predictions.

    Parameters:
    - race_id (int): Identifier for the race.
    - coeficients_for_predictions (list[float], optional): List of coefficients for generating predictions. Default set to [0.0].
    - logg_level (str|None, optional): Logging level for the race logger. Default set to "WARNING" level.
    - how_many_digits_after_period_to_leave_in (int, optional): Number of digits to round floating-point values to. Default set to 4 digits.
    - margin_in_seconds_to_add_to_mean_time (int, optional): Margin in seconds to add to the mean lap time. Default set to 5 seconds.
    - regression_models_instances (list, optional): List of regression model instances for prediction. 
    Default contains: regression_models.MultipleLinearRegression_, regression_models.PolinomialRegression_, regression_models.SupportVectorRegression_, regression_models.DecisionTreeRegression_, regression_models.RandomForestRegression_.
    - minimum_value_to_r2 (float, optional): Minimum R2 score threshold for regression models. Default set to 0.0.
    - size_of_test_set (float, optional): Size of the test set during regression model evaluation. Default set to  0.15 (15%).
    - set_n_splits (int): Number of splits for ShuffleSplit.
    - train_test_split_random_state (int, optional): Random state for train-test splitting. Default set to 2 iterations.

    Returns:
    - dict: A dictionary containing the analyzed race data, including predictions and statistics.

    Note:
    - This function performs the following steps:
        1. Retrieves race records and creates a DataFrame.
        2. Cleans and filters the DataFrame, removing irrelevant data.
        3. Computes pilot and kart statistics based on the cleaned DataFrame.
        4. Generates predictions for tempo and fastest lap using regression models.
        5. Formats and organizes the results into a structured dictionary.
    
    - The function utilizes a logging system to record the process details if a logging level is specified.
    
    - The generated statistics include information about each kart, its fastest lap, tempo, and associated pilots.
    
    - Predictions for tempo and fastest lap are generated using specified regression models.
    """
    # Set up the logger for the race
    if logg_level is not None:
        logger_set_up_start_timer = time.perf_counter()
        
        # Create logger to make logs
        race_logger = logging_initialization.get_or_create_logger_for_race(
            race_id = race_id,
            log_level = logg_level
        )
                
        # FileHandler change for logger, to change logger location
        file_handler = logging_initialization.create_and_assign_filehandler_to_logger(
            race_logger = race_logger,
            race_id=race_id
        )
        
        logger_set_up_end_time = time.perf_counter()
        
        race_logger.debug(f"{logger_set_up_end_time-logger_set_up_start_timer} secons took logger to set up")
        race_logger.debug("START")
        
        start_timer = time.perf_counter()
    
    # 1. Retrieves race records and creates a DataFrame.
    try:
        # Attempt to create a DataFrame from recorded race records using the create_df_from_recorded_records function.
        # If no records are found for the specified race, a ValueError is raised, and the function returns a dictionary
        # indicating the race_id with an error message.
        df_from_recorded_records = laps_frame_creation.create_df_from_recorded_records(
            race_id=race_id
        )
    except ValueError:
        return {
            "race_id": race_id
        }

    
    # 2. Cleans and filters the DataFrame, removing irrelevant data.
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

    # 3. Computes pilot and kart statistics based on the cleaned DataFrame.
    df_pilots = statistic_creation.create_pilot_statistics(
        df_with_records=df_from_recorded_records,
    )

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
   
    df_stats = statistic_creation.merge_all_statistic_about_pilots_and_karts(
        df_with_each_kart_and_pilot_combo_statistic = df_pilot_on_karts,
        df_with_statistic_of_pilots = df_pilots,
        df_with_statistic_of_karts = df_karts,
    )
    
    list_with_predictions = [
        prediction_processing.generate_regression_prediction_input(
                coeficient,
                df_of_pilots=df_pilots.copy(),
                df_of_karts=df_karts.copy(),
            )
        for coeficient in coeficients_for_predictions
    ]

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
        return {
            "race_id": race_id
        }


    # 4. Generates predictions for tempo and fastest lap using regression models.
    # and
    # 5. Formats and organizes the results into a structured dictionary.
    
    return_dict = {
        "data": {    
            #"temp_predictions": [],
            #"temp_r2_scores": {},
            #"fastestlap_predictions": [],
            #"fastestlap_r2_scores": {},
        }
    } 

    series_of_karts = pd.Series(
        list_with_predictions[0].loc[:, "kart"].drop_duplicates().copy(),
        name="kart",
    )
    
    # Sequence number of columns to apply OneHotEncoding. It is set to be done on first column only
    SEQUENCE_NUMBER_OF_COLUMNS_TO_OHE = [0]

    if logg_level is not None:
        race_logger.debug("1. Temp")
    dicts_from_temp_predictions = regression_process.regression_process(
        df_to_analyze, list_with_predictions,
        
        logger_instance=race_logger,
        
        regression_models_instances=regression_models_instances,
        minimum_value_to_r2=minimum_value_to_r2,
        size_of_test_set=size_of_test_set,
        set_n_splits=set_n_splits,
        
        train_test_split_random_state=train_test_split_random_state,
        sequence_number_of_columns_to_OHE=SEQUENCE_NUMBER_OF_COLUMNS_TO_OHE,
        
        how_many_digits_after_period_to_leave_in = how_many_digits_after_period_to_leave_in
    ) 
    data = functions_for_return.form_return_after_analyzation_with_error_check(
        dict_with_predictions=dicts_from_temp_predictions,
        series_of_karts=series_of_karts,
        word_to_name_predictions_type="temp",
    )
    return_dict["data"].update(data)

    df_to_analyze.pop("temp_with_pilot")
    df_to_analyze["fastest_lap_with_pilot"] = df_stats.pop("fastest_lap_with_pilot")
    del df_stats

    if logg_level is not None:
        race_logger.debug("2. Fastest lap")
    dicts_from_fastestlap_predictions = regression_process.regression_process(
        df_to_analyze, list_with_predictions,
        
        logger_instance=race_logger,
        
        regression_models_instances=regression_models_instances,
        minimum_value_to_r2=minimum_value_to_r2,
        size_of_test_set=size_of_test_set,
        train_test_split_random_state=train_test_split_random_state,
        sequence_number_of_columns_to_OHE=SEQUENCE_NUMBER_OF_COLUMNS_TO_OHE,
        
        how_many_digits_after_period_to_leave_in = how_many_digits_after_period_to_leave_in
    )
    data = functions_for_return.form_return_after_analyzation_with_error_check(
        dict_with_predictions=dicts_from_fastestlap_predictions,
        series_of_karts=series_of_karts,
        word_to_name_predictions_type="fastestlap",
    )
    return_dict["data"].update(data)

    return_dict.update(
        {
            "race_id": race_id
        }
    )
    
    # Log the time taken by the function if logging is enabled
    if logg_level is not None:
        end_timer = time.perf_counter()
        race_logger.info(f"END:{end_timer-start_timer} seconds were used by whole analyzation process before finishing")
        race_logger.removeHandler(file_handler)
        

    return return_dict

