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
            yes -> changes all previous 0 kart records for this pilot to valid kart number
            no -> make a flag, to indicate all non valid kard records
                 + make a last team`s kart = 0
    
    Args:
        df_statistic (pd.DataFrame): DataFrame with all statistic of laps
        df_last_lap_info (pd.DataFrame): DataFrame with info about team last state
        team (str): Team, which kart we are cheking
        kart (int): Kart, which shown in the programme
        pilot_name (str): Name of a pilot to look for

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

def name_check_after_pit(
    df_statistic: pd.DataFrame,
    df_last_lap_info: pd.DataFrame,
    team: str,
    seconds_from_pit: int,
    pilot_name: str,
    
    seconds_to_pass:int = 540
) -> bool:
    """Check if team made set amount of time on track after the pit or start:
            yes -> change all names  before this point on the current segment to the current name
            no -> set a flag to indicate vrong name 

    Args:
        df_statistic (pd.DataFrame): DataFrame with all statistic of laps
        df_last_lap_info (pd.DataFrame): DataFrame with info about team last state
        team (str): Team that we are checking
        seconds_from_pit (int): Amount of seconds after last pit of the team
        pilot_name (str): Name of a pilot that we are changing 
        seconds_to_pass (int, optional): amount of seconds, that needs to pass after the start, for name to become valid. Defaults to 540.
    
    Returns:
        bool: True, if set amout of seconds passed after the last pit
    """
    if  seconds_from_pit >= 540:
        true_name = True
        if (df_last_lap_info.loc[team, "was_on_pit"] == True):
            needed_indexes = df_statistic[
                (df_statistic.loc[:,"team"] == team) 
                &(df_statistic.loc[:,"true_name"] == False) 
                &(
                    df_statistic.loc[:,"segment"] ==\
                        df_last_lap_info.loc[team, "current_segment"]
                )
            ].index
            df_statistic.loc[needed_indexes, "true_name"] = True
            df_statistic.loc[needed_indexes, "pilot"] = pilot_name
            df_last_lap_info.loc[team, "was_on_pit"] = False
    else:
        true_name = False
    
    return true_name
            
def check_is_team_on_pit(
    is_on_pit: bool,
    df_last_lap_info: pd.DataFrame,
    team: str
) -> None:
    """Check if isOnPit flag is True:
            yes -> change team`s flag was_on_pit to true
            + if it is 1st encounter -> add to segment and renew segment for the team  

    Args:
        is_on_pit (bool): Flag, that indicate if team is on pit
        df_last_lap_info (pd.DataFrame): DataFrame with info about team last state
        team (str): Team, for which we changing it state 
    """
    if is_on_pit:
        if df_last_lap_info.loc[team, "was_on_pit"] == False:
            df_last_lap_info.loc[team, "current_segment"] += 1
        df_last_lap_info.loc[team, "was_on_pit"] = True