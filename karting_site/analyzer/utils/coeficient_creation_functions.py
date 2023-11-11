import numpy as np
import pandas as pd
import time

from analyzer import models

def create_primary_coeficient ():
    st_t = time.perf_counter()

    individual_pilot_statistic_df = pd.DataFrame(
        {
            "pilot": pd.Series(dtype=str)
        }
    )
    
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
    
    for race in races:
        race_query = models.TempOfPilotsInBR.objects.filter(race = race.id).values_list()
        race_statistic_df = pd.DataFrame.from_records(
            race_query, 
            columns=[
                "id",
                "race_id",
                "pilot",
                "average_lap_time"
            ]
        )
       
        race_statistic_df.pop("id")
        race_statistic_df.pop("race_id")
        
        column_name = f"race_{race.id}"
        
        for pilot in race_statistic_df.loc[:, "pilot"]:
            lap_time = race_statistic_df.loc[
                race_statistic_df.loc[:, "pilot"] == pilot,
                "average_lap_time"
            ].reset_index(drop=True)
            needed_index = individual_pilot_statistic_df[
                (individual_pilot_statistic_df.loc[:,"pilot"] == pilot)
            ].index
            if not needed_index.empty:
                individual_pilot_statistic_df.loc[
                    needed_index,
                    column_name
                ] = lap_time[0]
            else:
                individual_pilot_statistic_df.loc[len(individual_pilot_statistic_df.index), "pilot"]=pilot
                individual_pilot_statistic_df.loc[
                    individual_pilot_statistic_df.loc[:, "pilot"] == pilot,
                    column_name
                ] = lap_time[0]
                
    for race_as_column in individual_pilot_statistic_df:
        if race_as_column != "pilot":
            individual_pilot_statistic_df[race_as_column] =\
                column_with_lap_time_to_coeficient(
                    individual_pilot_statistic_df.loc[:,race_as_column].copy()
                )

    for index in individual_pilot_statistic_df.loc[:, "pilot"].index:
        average_pilot_coeficient = individual_pilot_statistic_df.iloc[index, 1:-1].mean()
        average_pilot_coeficient = float(f"{average_pilot_coeficient:.4f}")
        individual_pilot_statistic_df.loc[index, "coeficient"] = average_pilot_coeficient

    individual_pilot_statistic_df = pd.DataFrame(
        {
            "pilot": individual_pilot_statistic_df["pilot"],
            "coeficient": individual_pilot_statistic_df["coeficient"]
        }
    )

    en_t = time.perf_counter()
    print(en_t-st_t)
    return individual_pilot_statistic_df

def column_with_lap_time_to_coeficient(
    column_to_transform: pd.Series
):
    max_temp = column_to_transform.max()
    min_temp = column_to_transform.min()
    for temp in range(len(column_to_transform)):
        normilezed_temp =(
            (column_to_transform.loc[temp]-min_temp)
            /
            (max_temp-min_temp)
        )
        normilezed_temp = float(f"{normilezed_temp:.4f}")
        column_to_transform.at[temp] = normilezed_temp
    return column_to_transform

def get_pilot_coeficient_from_df_of_primary_coeficient(
    df_to_create_coeficients_into: pd.DataFrame,
    df_of_primary_coeficient: pd.DataFrame,
    
    pilot_index_in_df_to_create_coeficients_into:list,
    pilot: str
) -> list:
    this_race_coeficient = df_of_primary_coeficient.loc[
                df_of_primary_coeficient.loc[:, "pilot"] == pilot,
                "coeficient"
            ]
    if not this_race_coeficient.empty:
        return this_race_coeficient.values
    else:
        this_race_coeficient = df_to_create_coeficients_into.loc[
            pilot_index_in_df_to_create_coeficients_into,
            "this_race_coeficient"
        ]
        return this_race_coeficient.values

def create_avarage_coeficient(
    this_race_coeficient: float,
    pilot_coeficient: float,
) -> float:
    average_coeficient = (
            this_race_coeficient
        +
            pilot_coeficient
        )/2 
    return average_coeficient

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
    df_to_create_coeficients_into["this_race_coeficient"] = column_with_lap_time_to_coeficient(
        df_to_create_coeficients_into.loc[:,"pilot_temp"].copy()
    )
    
    max_temp = df_to_create_coeficients_into["pilot_temp"].max()
    min_temp = df_to_create_coeficients_into["pilot_temp"].min()
    
    for pilot in df_to_create_coeficients_into.loc[:, "pilot"]:
        pilot_index_in_df_to_create_coeficients_into = df_to_create_coeficients_into.loc[
                df_to_create_coeficients_into.loc[:, "pilot"] == pilot,
                "pilot"
            ].index
        df_to_create_coeficients_into.loc[
                pilot_index_in_df_to_create_coeficients_into,
                "pilot_coeficient"
        ] = get_pilot_coeficient_from_df_of_primary_coeficient(
            df_to_create_coeficients_into=df_to_create_coeficients_into,
            df_of_primary_coeficient=df_of_primary_coeficient,
            
            pilot_index_in_df_to_create_coeficients_into=pilot_index_in_df_to_create_coeficients_into,
            pilot=pilot
        )

        df_to_create_coeficients_into.loc[
            pilot_index_in_df_to_create_coeficients_into,
            "average_coeficient"
        ] = create_avarage_coeficient(
            this_race_coeficient=df_to_create_coeficients_into.loc[
                    pilot_index_in_df_to_create_coeficients_into,
                    "this_race_coeficient"
                ],
            pilot_coeficient=df_to_create_coeficients_into.loc[
                    pilot_index_in_df_to_create_coeficients_into,
                    "pilot_coeficient"
                ]
        ) 

        df_to_create_coeficients_into.loc[
            pilot_index_in_df_to_create_coeficients_into,
            "temp_from_average_coeficient"
        ] = make_temp_from_average_coeficient(
            average_coeficient=df_to_create_coeficients_into.loc[
                    pilot_index_in_df_to_create_coeficients_into,
                    "average_coeficient"
                ],
            max_temp=max_temp,
            min_temp=min_temp
        )
    return df_to_create_coeficients_into