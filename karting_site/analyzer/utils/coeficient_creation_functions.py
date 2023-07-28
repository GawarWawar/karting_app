import numpy as np
import pandas as pd

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