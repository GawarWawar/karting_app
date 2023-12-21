import numpy as np
import pandas as pd

import time
import logging

from analyzer import models as analyzer_models

from . import statistic_creation
from . import models_transmissions

def normalize_temp(
    pilot_temp: float,
    
    max_temp:float,
    min_temp:float,
    
    how_many_digits_after_period_to_leave_in:int = 4
):
    """
    Normalize the race tempo within a specified range.

    This function calculates the normalized tempo based on the given race tempo,
    maximum tempo, and minimum tempo. The normalization is performed using the formula:

    normalized_tempo = (tempo - min_tempo) / (max_tempo - min_tempo)

    Parameters:
    - pilot_temp (float): The race tempo of pilot to be normalized.
    - max_tempo (float): The maximum tempo in the range.
    - min_tempo (float): The minimum tempo in the range.
    - how_many_digits_after_period_to_leave_in (int, optional): The number of digits to round the
      normalized tempo to after the decimal point. Default is 4.

    Returns:
    - float: The normalized race tempo within the specified range.
    """
    normilezed_temp =(
        (pilot_temp-min_temp)
        /
        (max_temp-min_temp)
    )
    normilezed_temp = float(f"{normilezed_temp:.{how_many_digits_after_period_to_leave_in}f}")

    return normilezed_temp

def create_primary_coeficient (
    
    how_many_digits_after_period_to_leave_in:int = 4,
    logger_instance: logging.Logger|None = None,
):
    """
    Create and normalize primary coefficients for each pilot based on race tempo.

    This function retrieves race data, calculates coefficients for each pilot based on their
    average lap times, normalizes the coefficients, and aggregates the results.

    Parameters:
    - how_many_digits_after_period_to_leave_in (int, optional): The number of digits to round the
      normalized coefficients to after the decimal point. Default is 4.
    - logger_instance (logging.Logger | None, optional): An optional logger instance to log
      performance information. Default is None.

    Returns:
    - pd.DataFrame: A DataFrame containing the primary coefficients for each pilot.

    Note:
    If no races are found, an empty DataFrame with columns 'pilot_name' and 'coeficient' is
    returned.
    """
    if logger_instance is not None:
        start_timer = time.perf_counter()
    
    races = analyzer_models.BigRace.objects.all()
    
    if not races:
        individual_pilot_statistic_df = pd.DataFrame(
            {
                "pilot_name": pd.Series(dtype=str),
                "coeficient": pd.Series(dtype=float)
            }
        )
        if logger_instance is not None:
            end_timer = time.perf_counter()
            logger_instance.debug(f"{end_timer-start_timer} seconds seconds were used by 'create_primary_coeficient' (no races were found)")
        return individual_pilot_statistic_df
    else:
        individual_pilot_statistic_df = pd.DataFrame(
            {
                "pilot_name": pd.Series(dtype=str)
            }
        )
    
    for big_race in races:
        this_race_statistic_df = models_transmissions.collect_model_records_into_DataFrame(
            model = analyzer_models.TempOfPilotsInBR,
            inheritance_id = big_race.id,
            column_of_inheritance_id="race",
            purge_models_technical_columns=True
        )
        
        max_temp = this_race_statistic_df["average_lap_time"].max()
        min_temp = this_race_statistic_df["average_lap_time"].min()
        
        this_race_statistic_df["coeficient"] =\
            this_race_statistic_df["average_lap_time"].apply(
                normalize_temp,
                max_temp = max_temp,
                min_temp = min_temp,
                how_many_digits_after_period_to_leave_in = how_many_digits_after_period_to_leave_in
            )

        individual_pilot_statistic_df = pd.concat(
            [individual_pilot_statistic_df, this_race_statistic_df]
        )

    individual_pilot_statistic_df = statistic_creation.module_to_create_df_with_statistic(
        df_of_records=individual_pilot_statistic_df,
        
        df_with_features=individual_pilot_statistic_df.drop_duplicates("pilot"),
        column_of_the_lable="pilot",
        
        column_to_look_for_value_of_the_lable="coeficient",
        
        mean = "average_coeficient"
    )

    individual_pilot_statistic_df = pd.DataFrame(
        {
            "pilot_name": individual_pilot_statistic_df["pilot"],
            "coeficient": individual_pilot_statistic_df["average_coeficient"]
        }
    )
    
    if logger_instance is not None:
        end_timer = time.perf_counter()
        logger_instance.debug(f"{end_timer-start_timer} seconds were used by 'create_primary_coeficient'")
    return individual_pilot_statistic_df

def make_temp_from_average_coeficient(
    average_coeficient: float,
    max_temp: float,
    min_temp: float
) -> float:
    """
    Calculate tempo from the average coefficient.

    This function takes the average coefficient for a pilot, along with the maximum and minimum
    tempos in a given range, and calculates the corresponding tempo.

    Parameters:
    - average_coeficient (float): The average coefficient for a pilot.
    - max_tempo (float): The maximum tempo in the range.
    - min_tempo (float): The minimum tempo in the range.

    Returns:
    - float: The calculated tempo from the average coefficient.

    Note:
    The formula used for calculation is: tempo_from_average_coeficient = (average_coeficient *
    (max_tempo - min_tempo)) + min_tempo
    """
    temp_from_average_coeficient = (
                average_coeficient
            *
                (
                    max_temp
                -
                    min_temp
                )
            ) + min_temp
    return temp_from_average_coeficient
        

def add_coeficients_and_temp_from_average_coeficient_to_df (
    df_to_create_coeficients_into: pd.DataFrame,
    df_of_primary_coeficient: pd.DataFrame,
    
    how_many_digits_after_period_to_leave_in:int = 4,
    logger_instance: logging.Logger|None = None,
):
    """
    Add coefficients and tempo from average coefficient to a DataFrame.

    This function calculates the race coefficients and average coefficients for each pilot
    based on their tempo and merges the results with a DataFrame containing primary coefficients.

    Parameters:
    - df_to_create_coeficients_into (pd.DataFrame): The DataFrame to add coefficients and
      tempo information to.
    - df_of_primary_coeficient (pd.DataFrame): The DataFrame containing primary coefficients
      for each pilot.
    - how_many_digits_after_period_to_leave_in (int, optional): The number of digits to round the
      normalized coefficients to after the decimal point. Default is 4.
    - logger_instance (logging.Logger | None, optional): An optional logger instance to log
      performance information. Default is None.

    Returns:
    - pd.DataFrame: The modified DataFrame with added coefficients and tempo information.

    Note:
    The input DataFrame 'df_to_create_coeficients_into' is expected to contain a 'pilot_temp'
    column representing the pilot tempo.

    The resulting DataFrame will have additional columns:
    - 'this_race_coeficient': The normalized coefficient for each pilot based on their tempo
      in the current race.
    - 'coeficient': The primary coefficient for each pilot (taken from 'df_of_primary_coeficient').
    - 'average_coeficient': The average of 'this_race_coeficient' and 'coeficient' for each pilot.
    - 'temp_from_average_coeficient': The tempo calculated from the 'average_coeficient'.
    """
    if logger_instance is not None:
        start_timer = time.perf_counter()
    
    max_temp = df_to_create_coeficients_into["pilot_temp"].max()
    min_temp = df_to_create_coeficients_into["pilot_temp"].min()
    
    df_to_create_coeficients_into["this_race_coeficient"] =\
       df_to_create_coeficients_into["pilot_temp"].apply(
                normalize_temp,
                max_temp = max_temp,
                min_temp = min_temp,
                how_many_digits_after_period_to_leave_in = how_many_digits_after_period_to_leave_in
            )
    
    df_to_create_coeficients_into = pd.merge(
        df_to_create_coeficients_into,
        df_of_primary_coeficient,
        on="pilot_name",
        how="left",
    )
    
    df_to_create_coeficients_into.coeficient.fillna(
        df_to_create_coeficients_into.this_race_coeficient, 
        inplace=True
    )
    
    df_to_create_coeficients_into["average_coeficient"] = \
        df_to_create_coeficients_into[
            ['this_race_coeficient', 'coeficient']
        ].mean(axis=1)
    
    df_to_create_coeficients_into["temp_from_average_coeficient"] =\
        df_to_create_coeficients_into["average_coeficient"].apply(
            make_temp_from_average_coeficient,
            max_temp = max_temp,
            min_temp = min_temp
        )
    
    if logger_instance is not None:
        end_timer = time.perf_counter()
        logger_instance.debug(f"{end_timer-start_timer} seconds were used by 'add_coeficients_and_temp_from_average_coeficient_to_df'")
    
    return df_to_create_coeficients_into