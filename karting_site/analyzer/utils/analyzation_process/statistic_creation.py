import pandas as pd
import numpy as np

import time

def module_to_create_df_with_statistic(
    df_of_records: pd.DataFrame, 
    
    df_with_features: pd.DataFrame,
    column_of_the_lable: str,
    
    column_to_look_for_value_of_the_lable: str,
    
    **kwargs
) -> pd.DataFrame:
    """
    Perform aggregation on a DataFrame based on a specified label column, 
    and merge the aggregated values with another DataFrame.

    Parameters:
    - df_of_records (pd.DataFrame): DataFrame containing records to be aggregated.
    - df_with_features (pd.DataFrame): DataFrame to be updated with aggregated statistics.
    - column_of_the_lable (str): Column in df_of_records used to identify unique labels.
    - column_to_look_for_value_of_the_lable (str): Column in df_of_records where values are used for aggregation.
    - **kwargs: Keyword arguments specifying aggregation functions and corresponding new column names.
      Example: mean='mean_column_name', min='min_column_name'

    Returns:
    pd.DataFrame: Updated DataFrame with aggregated statistics.
    """
    
    # Group by the specified feature column
    grouped_records = df_of_records.groupby(
        column_of_the_lable
    )

    for agg_func_to_perform in kwargs:
        new_column = kwargs.get(agg_func_to_perform)
        
        if new_column is not None:
            changed_values = grouped_records[
                column_to_look_for_value_of_the_lable
            ].agg(agg_func_to_perform).T.to_frame()

        
        changed_values = changed_values.rename(
            columns={
                column_to_look_for_value_of_the_lable : new_column
            },
            inplace=False
        )
        
        df_with_features = df_with_features.merge(
            changed_values,  
            on=column_of_the_lable)

    return df_with_features

def module_to_create_pilot_statistics (
    df_of_records: pd.DataFrame,
):
    df_of_pilots = df_of_records.loc[
        (df_of_records.loc[:, "true_name" ]== True), 
        "pilot"
    ].drop_duplicates().copy().T.to_frame()
    df_of_pilots = df_of_pilots.reset_index(drop=True)
    
    # df_of_pilots["pilot_temp"] = 0
    # df_of_pilots["pilot_fastest_lap"] = 0
    
    df_of_pilots = module_to_create_df_with_statistic(
        df_of_records=df_of_records,
        
        df_with_features=df_of_pilots,
        column_of_the_lable="pilot",
        
        column_to_look_for_value_of_the_lable="lap_time",
        
        mean="pilot_temp",
        min="pilot_fastest_lap",
    )
        
    return df_of_pilots

def module_to_create_kart_statistics (
    df_of_records: pd.DataFrame,
):  
    df_of_karts = df_of_records.loc[
        df_of_records.loc[:, "true_kart" ]== True,
        "kart"
    ].drop_duplicates().T.to_frame()
    
    # df_of_karts["kart_temp"] = 0
    # df_of_karts["kart_fastest_lap"] = 0
    
    df_of_karts = module_to_create_df_with_statistic(
        df_of_records=df_of_records,
        
        df_with_features=df_of_karts,
        column_of_the_lable="kart",
        
        column_to_look_for_value_of_the_lable="lap_time",
        
        mean="kart_temp",
        min="kart_fastest_lap",
    )
    
    return df_of_karts

def module_to_create_karts_statistics_for_every_pilot(
    df_of_records: pd.DataFrame,
):
    # WORKS ONLY IF df_of_records DOESNT HAVE:
    # true_kart == False
    # true_name == False (recomended, not mandatory)
    df_of_records.pop("team")
    
    df_pilot_on_karts = pd.DataFrame(
        {
            "pilot": pd.Series(dtype=str),
            "kart": pd.Series(dtype=str),
            "temp_with_pilot": pd.Series(dtype=float),
            "fastest_lap_with_pilot": pd.Series(dtype=float),   
        }
    )
    
    df_pilot_on_karts["temp_with_pilot"] = 0
    df_pilot_on_karts["fastest_lap_with_pilot"] = 0

    groups = df_of_records.groupby("pilot").groups
    
    for group in groups:
        all_pilot_kart_records = df_of_records.loc[
            df_of_records.loc[:,"pilot"] == group,
            :
        ]
        all_pilot_kart_records.pop("true_name")
        all_pilot_kart_records.pop("true_kart")
        
        karts_of_pilot_df = module_to_create_df_with_statistic(
            df_of_records=all_pilot_kart_records,

            df_with_features = all_pilot_kart_records.drop_duplicates("kart"),
            column_of_the_lable="kart",

            column_to_look_for_value_of_the_lable="lap_time",
            
            mean="temp_with_pilot",
            min="fastest_lap_with_pilot",
        )
        
        karts_of_pilot_df.pop("lap_time")
        karts_of_pilot_df.pop("s1")
        karts_of_pilot_df.pop("s2")

        df_pilot_on_karts = pd.concat(
            [df_pilot_on_karts, karts_of_pilot_df]   
        )
    
    return df_pilot_on_karts



def module_to_create_karts_statistics_for_every_pilot_old(
    df_of_records: pd.DataFrame,
):
    df_of_records.pop("team")
    
    df_pilot_on_karts = pd.DataFrame(
        {
            "pilot": pd.Series(dtype=str),
            "kart": pd.Series(dtype=str),
            "temp_with_pilot": pd.Series(dtype=float),
            "fastest_lap_with_pilot": pd.Series(dtype=float),   
        }
    )
    
    df_pilot_on_karts["temp_with_pilot"] = 0
    df_pilot_on_karts["fastest_lap_with_pilot"] = 0
    
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
            column_of_the_lable="kart",

            column_to_look_for_value_of_the_lable="lap_time",
            column_name_to_put_mean_value_in="temp_with_pilot",
            column_name_to_put_min_value_in="fastest_lap_with_pilot",
        )

        karts_of_pilot_df.pop("lap_time")
        karts_of_pilot_df.pop("s1")
        karts_of_pilot_df.pop("s2")


        df_pilot_on_karts = pd.concat(
            [df_pilot_on_karts, karts_of_pilot_df]   
        )
    return df_pilot_on_karts

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