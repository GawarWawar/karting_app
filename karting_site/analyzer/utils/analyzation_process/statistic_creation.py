import pandas as pd
import numpy as np

import time

def module_to_create_df_with_statistic(
    df_of_records: pd.DataFrame, 
    
    df_with_features: pd.DataFrame,
    column_of_the_label: str,
    
    column_to_look_for_value_of_the_lable: str,
    
    **kwargs
) -> pd.DataFrame:
    """
    Perform aggregation on a DataFrame based on a specified label column,
    and merge the aggregated values with another DataFrame.

    Parameters:
    - df_of_records (pd.DataFrame): DataFrame containing records to be aggregated.
    - df_with_features (pd.DataFrame): DataFrame to be updated with aggregated statistics.
    - column_of_the_label (str): Column in df_of_records used to identify unique labels.
    - column_to_look_for_value_of_the_label (str): Column in df_of_records where values are used for aggregation.
    - **kwargs: Keyword arguments specifying aggregation functions and corresponding new column names.
      Example: mean='mean_column_name', min='min_column_name'

    Returns:
    - pd.DataFrame: Updated DataFrame with aggregated statistics.
    """
    
    # Group by the specified label column
    grouped_records = df_of_records.groupby(
        column_of_the_label
    )

    for agg_func_to_perform in kwargs:
        # Aggregate values based on the specified function
        new_column = kwargs.get(agg_func_to_perform)
        
        changed_values = grouped_records[
            column_to_look_for_value_of_the_lable
        ].agg(agg_func_to_perform).T.to_frame()

        # Rename the aggregated column for clarity
        changed_values = changed_values.rename(
            columns={
                column_to_look_for_value_of_the_lable : new_column
            },
            inplace=False
        )
        
        # Merge the aggregated values with the features DataFrame
        df_with_features = df_with_features.merge(
            changed_values,  
            on=column_of_the_label)

    return df_with_features


def create_statistic_module_for_certain_column_in_df_with_records (
    df_with_records: pd.DataFrame,
    column_to_create_module_on: str,
    
    column_to_look_for_value_of_the_lable:str = "lap_time",
    
    **kwargs
) -> pd.DataFrame:
    """
    Create a statistical module for a specific column in a DataFrame with records.

    This function generates a statistical module based on a specified label column in a DataFrame
    containing records. The module includes aggregated statistics for the chosen column and can be
    used for both kart and pilot statistics. Note that it works properly only if the input DataFrame
    does not have 'true_kart' set to False (for kart statistics) or 'true_name' set to False
    (for pilot statistics).

    Parameters:
    - df_with_records (pd.DataFrame): DataFrame containing records to create the statistical module.
    - column_to_create_module_on (str): Column in df_with_records to create the statistical module on.
    - column_to_look_for_value_of_the_label (str): Column in df_with_records where values are used for aggregation.
      Default is 'lap_time'.
    - **kwargs: Keyword arguments specifying aggregation functions and corresponding new column names.
      Example: mean='mean_column_name', min='min_column_name'

    Returns:
    - pd.DataFrame: Statistical module for the specified column in df_with_records.

    Note:
    The function drops duplicate values from the specified column, creates a statistical module
    using module_to_create_df_with_statistic, and returns the resulting DataFrame.
    """
    # WORKS properly ONLY IF df_of_records DOESNT HAVE:
        # true_kart == False (for karts` statistic)
        # true_name == False (for pilots` statistic)
        
    # Drop duplicates from the specified column
    df_with_statistic = df_with_records.loc[
        :, 
        column_to_create_module_on
    ].drop_duplicates().T.to_frame()
    df_with_statistic = df_with_statistic.reset_index(drop=True)
    
    # Create the statistical module using module_to_create_df_with_statistic
    df_with_statistic = module_to_create_df_with_statistic(
        df_of_records=df_with_records,
        
        df_with_features=df_with_statistic,
        column_of_the_label=column_to_create_module_on,
        
        column_to_look_for_value_of_the_lable=column_to_look_for_value_of_the_lable,
        
        **kwargs
    )
        
    return df_with_statistic

def create_pilot_statistics (
    df_with_records: pd.DataFrame,
):
    """
    Create statistics for pilots based on a DataFrame with records.

    This function generates statistical information for pilots based on a DataFrame with records.
    The resulting DataFrame includes aggregated statistics such as mean pilot tempo and
    minimum pilot fastest lap time.

    Parameters:
    - df_with_records (pd.DataFrame): DataFrame containing records to create pilot statistics.

    Returns:
    - pd.DataFrame: Statistical module for pilots with aggregated information.

    Note:
    The function internally uses create_statistic_module_for_certain_column_in_df_with_records to
    create statistics for the 'pilot_name' column, including mean pilot tempo and minimum
    pilot fastest lap time. The resulting DataFrame provides aggregated information for each pilot.
    """
    df_of_pilots = create_statistic_module_for_certain_column_in_df_with_records(
        df_with_records=df_with_records,
        column_to_create_module_on="pilot_name",
        
        mean="pilot_temp",
        min="pilot_fastest_lap" 
    )
    
    return df_of_pilots

def create_kart_statistics (
    df_with_records: pd.DataFrame,
):  
    """
    Create statistics for karts based on a DataFrame with records.

    This function generates statistical information for karts based on a DataFrame with records.
    The resulting DataFrame includes aggregated statistics such as mean kart tempo and
    minimum kart fastest lap time.

    Parameters:
    - df_with_records (pd.DataFrame): DataFrame containing records to create kart statistics.

    Returns:
    - pd.DataFrame: Statistical module for karts with aggregated information.

    Note:
    The function internally uses create_statistic_module_for_certain_column_in_df_with_records to
    create statistics for the 'kart' column, including mean kart tempo and minimum kart
    fastest lap time. The resulting DataFrame provides aggregated information for each kart.
    """
    df_of_karts = create_statistic_module_for_certain_column_in_df_with_records(
        df_with_records=df_with_records,
        column_to_create_module_on="kart",
        
        mean="kart_temp",
        min="kart_fastest_lap"
    )
    
    return df_of_karts

def module_to_create_karts_statistics_for_every_pilot(
    df_of_records: pd.DataFrame,
) -> pd.DataFrame:
    """
    Create statistics for karts for every pilot based on a DataFrame with records.

    This function generates statistical information for each kart associated with every pilot
    based on a DataFrame with records. The resulting DataFrame includes aggregated statistics such
    as mean kart tempo and minimum kart fastest lap time for each pilot.

    Parameters:
    - df_of_records (pd.DataFrame): DataFrame containing records to create karts statistics.

    Returns:
    - pd.DataFrame: Statistical module for karts with aggregated information for every pilot.

    Note:
    The function internally uses module_to_create_df_with_statistic to create statistics for each pilot's
    karts, including mean kart tempo and minimum kart fastest lap time. The resulting DataFrame
    provides aggregated information for every kart associated with each pilot.
    """
    
    # WORKS ONLY properly IF df_of_records DOESNT HAVE:
        # true_kart == False
        # true_name == False (recomended, not mandatory)
        
    # Drop unnecessary columns for better processing
    df_of_records = df_of_records.drop(
            columns=[
                "team_number", "true_name", "true_kart"
            ],
            inplace=False
        ).copy()
    
    # Initialize a DataFrame for pilot statistics on karts
    # Note:
        # Could be changed to df_pilot_on_karts = pd.DataFrame()
        # Will leave it here for now, to specify Dtypes
    df_pilot_on_karts = pd.DataFrame(
        {
            "pilot_name": pd.Series(dtype=str),
            "kart": pd.Series(dtype=str),
            "temp_with_pilot": pd.Series(dtype=float),
            "fastest_lap_with_pilot": pd.Series(dtype=float),   
        }
    )
    
    for pilot_name, pilot_records in df_of_records.groupby("pilot_name"):
        # Create statistics for each pilot's karts using module_to_create_df_with_statistic
        # Note:
            # df_of_records.groupby("pilot_name") returns tuple with:
                # 1st - Element of the column by which rows were groupped by
                # 2nd - pd.DataFrame or pd.Series with groupped rows
            # SO: we dont need 1st element, but we dont want to use tuple ->
                # we are doing unpacking inside of for
        
        karts_of_pilot_df = module_to_create_df_with_statistic(
            df_of_records=pilot_records,

            df_with_features=pilot_records.drop_duplicates("kart"),
            column_of_the_label="kart",
            
            column_to_look_for_value_of_the_lable="lap_time",
            
            mean="temp_with_pilot",
            min="fastest_lap_with_pilot",
        )
        
        # Drop unnecessary columns for better clarity
        karts_of_pilot_df.pop("lap_time")
        karts_of_pilot_df.pop("s1_time")
        karts_of_pilot_df.pop("s2_time")

        # Concatenate the results for each pilot
        df_pilot_on_karts = pd.concat(
            [df_pilot_on_karts, karts_of_pilot_df]   
        )
    
    return df_pilot_on_karts



def module_to_create_karts_statistics_for_every_pilot_old(
    df_of_records: pd.DataFrame,
):
    """
    Create statistics for karts for every pilot based on a DataFrame with records (legacy version).

    This function generates statistical information for each kart associated with every pilot
    based on a DataFrame with records. The resulting DataFrame includes aggregated statistics such
    as mean kart tempo and minimum kart fastest lap time for each pilot. Note that this is a
    legacy version of the function, and it is recommended to use the updated version
    (module_to_create_karts_statistics_for_every_pilot) for improved functionality.

    Parameters:
    - df_of_records (pd.DataFrame): DataFrame containing records to create karts statistics.

    Returns:
    - pd.DataFrame: Statistical module for karts with aggregated information for every pilot.

    Note:
    This legacy version drops 'team_number' from the input DataFrame, initializes a DataFrame for
    pilot statistics on karts, and iterates through each pilot to create kart statistics. The function
    utilizes module_to_create_df_with_statistic for aggregation.
    """
    df_of_records.pop("team_number")
    
    df_pilot_on_karts = pd.DataFrame(
        {
            "pilot_name": pd.Series(dtype=str),
            "kart": pd.Series(dtype=str),
            "temp_with_pilot": pd.Series(dtype=float),
            "fastest_lap_with_pilot": pd.Series(dtype=float),   
        }
    )
    
    df_pilot_on_karts["temp_with_pilot"] = 0
    df_pilot_on_karts["fastest_lap_with_pilot"] = 0
    
    for pilot in df_of_records.loc[
        (df_of_records.loc[:, "true_name" ]== True),
        "pilot_name"
    ].drop_duplicates():
        all_pilot_kart_records = df_of_records.loc[
            df_of_records.loc[:, "pilot_name"]==pilot,
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
            column_of_the_label="kart",

            column_to_look_for_value_of_the_lable="lap_time",
            column_name_to_put_mean_value_in="temp_with_pilot",
            column_name_to_put_min_value_in="fastest_lap_with_pilot",
        )

        karts_of_pilot_df.pop("lap_time")
        karts_of_pilot_df.pop("s1_time")
        karts_of_pilot_df.pop("s2_time")


        df_pilot_on_karts = pd.concat(
            [df_pilot_on_karts, karts_of_pilot_df]   
        )
    return df_pilot_on_karts

# NEED REWORK
def merge_all_statistic_about_pilots_and_karts(
    df_with_each_kart_and_pilot_combo_statistic: pd.DataFrame,
    df_with_statistic_of_pilots: pd.DataFrame,
    df_with_statistic_of_karts: pd.DataFrame
):
    """
    Merge statistical information about pilots and karts.

    This function merges statistical information about pilots and karts from different DataFrames,
    creating a comprehensive DataFrame that includes statistics for each pilot and associated kart.

    Parameters:
    - df_with_each_kart_and_pilot_combo_statistic (pd.DataFrame): DataFrame with statistics for each kart-pilot combo.
    - df_with_statistic_of_pilots (pd.DataFrame): DataFrame with aggregated statistics for pilots.
    - df_with_statistic_of_karts (pd.DataFrame): DataFrame with aggregated statistics for karts.

    Returns:
    - pd.DataFrame: Merged DataFrame with comprehensive statistics for pilots and karts.

    Note:
    The function performs three-way merging of statistical DataFrames based on 'pilot_name' and 'kart' columns.
    It resets the index, drops any rows with missing values, and returns the merged DataFrame with comprehensive statistics.
    """
    df_stats = pd.DataFrame.merge(
        df_with_each_kart_and_pilot_combo_statistic,
        df_with_statistic_of_pilots,
        on="pilot_name"
    )

    df_stats = pd.DataFrame.merge(
        df_stats,
        df_with_statistic_of_karts,
        on="kart"
    )

    df_stats = df_stats.reset_index(drop=True)
    df_stats = df_stats.dropna()   
    
    return df_stats