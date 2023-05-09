import pandas as pd
import numpy as np


def kart_check (
    df_statistic: pd.DataFrame,
    df_last_lap_info: pd.DataFrame,
    team: str,
    kart: int,
    pilot_name: str
) -> bool:
    """ Check if kart was changed on valid or it is still 0:
            #yes -> changes all previous 0 kart records for this pilot to valid kart number
            #no -> make a flag, to indicate all non valid kard records
                # + make a last team`s kart = 0
    
    Args:
        df_statistic (pd.DataFrame): DataFrame with all statistic of laps
        df_last_lap_info (pd.DataFrame): DataFrame with info about team last state
        team (str): Team, which kart we are cheking
        kart (int): Kart, which shown in the programme
        pilot_name (str): Pilot_name to look for

    Returns:
        bool: True, if it is valid kart number 
    """
    if kart == 0:
        true_kart = False
        df_last_lap_info.loc[team, "last_kart"] = kart
    else: 
        true_kart = True
        if kart != df_last_lap_info.loc[team, "last_kart"]:
            needed_indexes = df_statistic[
                (df_statistic.loc[:,"pilot"] == pilot_name) 
                &(df_statistic.loc[:,"true_kart"] == False) 
                &(df_statistic.loc[:,"kart"] == 0)
            ].index
            df_statistic.loc[needed_indexes, "true_kart"] = True
            df_statistic.loc[needed_indexes, "kart"] = kart
            df_last_lap_info.loc[team, "last_kart"] = kart
    return true_kart
