import numpy as np
import pandas as pd
import time

from analyzer import models

from . import statistic_creation
from . import models_transmissions

def normalize_temp(
    pilot_temp: float,
    
    max_temp:float,
    min_temp:float,
    
    how_many_digits_after_period_to_leave_in:int = 4
):
    normilezed_temp =(
        (pilot_temp-min_temp)
        /
        (max_temp-min_temp)
    )
    normilezed_temp = float(f"{normilezed_temp:.{how_many_digits_after_period_to_leave_in}f}")

    return normilezed_temp

def create_primary_coeficient ():
    st_t = time.perf_counter()
    
    races = models.BigRace.objects.all()
    
    if not races:
        individual_pilot_statistic_df = pd.DataFrame(
            {
                "pilot": pd.Series(dtype=str),
                "coeficient": pd.Series(dtype=float)
            }
        )
        en_t = time.perf_counter()
        print(en_t-st_t)
        return individual_pilot_statistic_df
    else:
        individual_pilot_statistic_df = pd.DataFrame(
            {
                "pilot": pd.Series(dtype=str)
            }
        )
    
    for big_race in races:
        this_race_statistic_df = models_transmissions.collect_BR_temp_records_into_DataFrame(
            race_id=big_race.id,
        )
        
        max_temp = this_race_statistic_df["average_lap_time"].max()
        min_temp = this_race_statistic_df["average_lap_time"].min()
        
        this_race_statistic_df["coeficient"] =\
            this_race_statistic_df["average_lap_time"].apply(
                normalize_temp,
                max_temp = max_temp,
                min_temp = min_temp
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
            "pilot": individual_pilot_statistic_df["pilot"],
            "coeficient": individual_pilot_statistic_df["average_coeficient"]
        }
    )

    en_t = time.perf_counter()
    print(en_t-st_t)
    return individual_pilot_statistic_df

def make_temp_from_average_coeficient(
    average_coeficient: float,
    max_temp: float,
    min_temp: float
) -> float:
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
    df_of_primary_coeficient: pd.DataFrame
):
    max_temp = df_to_create_coeficients_into["pilot_temp"].max()
    min_temp = df_to_create_coeficients_into["pilot_temp"].min()
    
    df_to_create_coeficients_into["this_race_coeficient"] =\
       df_to_create_coeficients_into["pilot_temp"].apply(
                normalize_temp,
                max_temp = max_temp,
                min_temp = min_temp
            )
    
    df_to_create_coeficients_into = pd.merge(
        df_to_create_coeficients_into,
        df_of_primary_coeficient,
        on="pilot",
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
    
    return df_to_create_coeficients_into