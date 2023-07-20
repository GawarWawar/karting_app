import pandas as pd
import numpy as np
import requests
from urllib3 import exceptions

import time

import sys
from os.path import dirname, abspath
import importlib.util
import logging

from . import add_row

def str_lap_time_into_float_change(
    lap_time: str
):
    try:
        lap_time = float(lap_time)
    except ValueError:
        split_lap_time = lap_time.split(":")
        lap_time = float(split_lap_time[0])*60+float(split_lap_time[1])
    return lap_time

def kart_check (
    df_last_lap_info: pd.DataFrame,
    team: str,
    kart: int,
) -> bool:
    """ Check if kart was changed on valid or it is still 0:
            yes -> make flag indicate that kart is valid;
            no -> make a flag, to indicate all non valid kard records;
                 + make a last team`s kart = 0.
    
    Args:
        df_last_lap_info (pd.DataFrame): DataFrame with info about team last state.\n
        team (str): Team, which kart we are cheking.\n
        kart (int): Kart, which shown in the programme.\n
    Returns:
        bool: True, if it is valid kart number.\n
    """
    if kart == 0:
        true_kart = False
        df_last_lap_info.loc[team, "last_kart"] = kart
    else: 
        true_kart = True
    return true_kart

def change_kart_on_true_value(
    df_statistic: pd.DataFrame,
    df_last_lap_info: pd.DataFrame,
    team: str,
    kart: int,
    logger: logging.Logger
):
    """ Check if it is true_kart and we didnt change it yet:
            changes all previous 0 kart records for this pilot to valid kart number;
            make a log about it;
    
    Args:
        df_statistic (pd.DataFrame): DataFrame with records of laps` statistic.\n
        df_last_lap_info (pd.DataFrame): DataFrame with info about team last state.\n
        team (str): Team, which kart we are cheking.\n
        kart (int): Kart, which shown in the programme.\n
        logging_file (str): Path to file in which we making log note about in what rows was kart changed.\n
    """
    if kart != df_last_lap_info.loc[team, "last_kart"]:
            needed_indexes = df_statistic[
                (df_statistic.loc[:,"team"] == team) 
                &(df_statistic.loc[:,"true_kart"] == False) 
                &(
                    df_statistic.loc[:,"segment"] ==\
                        df_last_lap_info.loc[team, "current_segment"]
                )
            ].index
            df_statistic.loc[needed_indexes, "true_kart"] = True
            df_statistic.loc[needed_indexes, "kart"] = kart
            df_last_lap_info.loc[team, "last_kart"] = kart
            
            logger.info(f"Rows with index: {needed_indexes} was changed for team {team} {df_last_lap_info.loc[team, 'current_segment']}'s segment to kart {kart}")

def set_name_flag_after_check_time_after_pit(
    seconds_from_pit: int,
    total_race_time: int,
    seconds_to_pass:int = 540
) -> bool:
    """Check if team made set amount of time on track after the pit or start:\n
            yes -> set name flag to True. It will represent, that name at this moment is true name;\n
            no -> set name flag to False. It will represent, that name at this moment is false name.\n
    Args:
        seconds_from_pit (int): Amount of seconds after last pit of the team.\n
        total_race_time (int): Amount of seconds that indicate how many seconds has passed after start of the race.\n
        seconds_to_pass (int, optional): amount of seconds, that needs to pass after the start, for name to become valid. Defaults is set to 540.\n
    
    Returns:
        bool: True, if set amout of seconds passed after the last pit.
    """
    if  seconds_from_pit >= seconds_to_pass and\
        total_race_time >= seconds_to_pass:
        true_name = True
    else:
        true_name = False
    
    return true_name

def change_name_to_true_name_after_the_pit (
    df_statistic: pd.DataFrame,
    df_last_lap_info: pd.DataFrame,
    team: str,
    pilot_name: str,
    logger: logging.Logger,
    true_name: bool,
    is_on_pit: bool
) -> None:
    """Change pilot name in all previous records of current segment if team left pit, on track set amount of seconds and this pocedure wasn't done after pit

    Args:
        df_statistic (pd.DataFrame): DataFrame with records of laps` statistic.\n
        df_last_lap_info (pd.DataFrame): DataFrame with info about team last state.\n
        team (str): Team that we are checking.\n
        pilot_name (str): Name of a pilot that we are changing.\n
        logging_file (str): Path to file in which we making log note about in what rows was kart changed.\n
        true_name (bool): Change name only if name is True already.\n
        is_on_pit (bool): Dont proceed to change pilots name if team is still on pit.\n
    """
    if (
        df_last_lap_info.loc[team, "was_on_pit"] == True
        and
        true_name
        and not
        is_on_pit
    ):
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
        
        logger.info(f"Rows with index: {needed_indexes} was changed for team {team} {df_last_lap_info.loc[team, 'current_segment']}'s segment to name {pilot_name}")

            
def set_was_on_pit_and_current_segment(
    is_on_pit: bool,
    df_last_lap_info: pd.DataFrame,
    team: str,
    teams_segment_count: int
) -> None:
    """Check if isOnPit flag is True:
            yes -> change team`s flag was_on_pit to true and renew segment for the team;

    Args:
        is_on_pit (bool): Flag, that indicate if team is on pit.\n
        df_last_lap_info (pd.DataFrame): DataFrame with info about team last state.\n
        team (str): Team, for which we changing it state.\n
        teams_segment_count (int): Current number of segments of the team.\n
    """
    if is_on_pit:
        df_last_lap_info.loc[team, "was_on_pit"] = True
        df_last_lap_info.loc[team, "current_segment"] = teams_segment_count
        
def add_lap_as_a_row(
    df_statistic: pd.DataFrame,
    df_last_lap_info: pd.DataFrame,
    teams_stats: dict,
    team: str,
    true_name: bool,
    true_kart: bool,
) -> None:
    """Add a row to df_statistic with a lap info. Also update lap count for team and make a log about it.

    Args:
        df_statistic (pd.DataFrame): DataFrame with records of laps` statistic.\n
        df_last_lap_info (pd.DataFrame): DataFrame with info about team last state.\n
        teams_stats (dict): Dictionary with all teams statistic for the current lap.\n
        team (str): Team we are making new record in df_statistic .\n
        true_name (bool): Flag, that indicate if team has a true kart already or should it be changed.\n
        true_kart (bool): Flag, that indicate if team has a true name already or should it be changed.\n
        logging_file (str): File, where logs are written.\n
    """ 
    
    add_row.add_a_row(
        df_statistic,
        [
            team, #team number in str
            teams_stats[team]["pilotName"], # pilot_name
            int(teams_stats[team]["kart"]), # kart
            teams_stats[team]["lapCount"], 
            teams_stats[team]["lastLap"], # lap_time
            teams_stats[team]["lastLapS1"], # s1
            teams_stats[team]["lastLapS2"], # s2
            df_last_lap_info.loc[team, "current_segment"], #team_segment
            true_name, # Flag to check if name is true and was changed after start or pit 
            true_kart, # Flag to check if kart is true or still 0
        ]
    )
    

def make_request_after_some_time(
    server: str,
    request_count: int,
    logger: logging.Logger,
    start_time_to_wait:float = time.perf_counter(),
    time_to_wait: int = 1
) -> tuple:
    """Check if set amount of time has passed after last request:
            yes -> make new request
            no -> wait for it to pass
        Also make a log about it

    Args:
        server (str): Link, on which we send a request.\n
        request_count (int): How many times we send request to the server. Needs to make a log about it.\n
        logging_file (str): File to paste logging info.\n
        start_time_to_wait (float, optional): Timestamp after the last request was done. Defaults is set to time.perf_counter().\n
        time_to_wait (int, optional): How much time do we need to wait before the next request. Defaults is set to 1 second.\n

    Returns:
        requests.Response: response did not get an exeption and we are getting response from the server\n
        None: we recieve one of the following exeptions: requests.exceptions.ReadTimeout, ConnectionResetError, exceptions.ProtocolError, requests.exceptions.ConnectionError
    """
    end_time_to_wait = time.perf_counter()
    if end_time_to_wait-start_time_to_wait < time_to_wait:
        while end_time_to_wait-start_time_to_wait < time_to_wait:
            end_time_to_wait = time.perf_counter()
    try: 
        server_request = requests.get(
            server, 
            timeout=10
        )
    except (requests.exceptions.ReadTimeout, ConnectionResetError, exceptions.ProtocolError, requests.exceptions.ConnectionError):
        end_time_to_wait = time.perf_counter()
        logger.info(
            f"While getting request numder {request_count} recieve exception. It took {end_time_to_wait-start_time_to_wait} time to get exception"
        )
        return None
    else:
        end_time_to_wait = time.perf_counter()
        logger.info(f"Request numder {request_count} took {end_time_to_wait-start_time_to_wait} time to get")
        return server_request
        
def make_request_until_its_successful(
    server: str,
    request_count: int,
    logger: logging.Logger,
    self,
    start_time_to_wait:float = time.perf_counter(),
    time_to_wait:int = 1
) -> tuple:
    """Call make_request_after_some_time and check if it was successful:\n
            yes -> return body of the response as a first variable;\n
            no -> try to call make_request_after_some_time until it gets valid response;\n
        As second variable return amount of requests that were needed.

    Args:
        server(str): Server, on which requests will be send
        request_count (int): How many times we sent requests already.\n
        logging_file (str): File to paste logging info. It is needed into make_request_after_some_time.\n
        start_time_to_wait (float, optional): Timestamp after the last request was done. It is needed into make_request_after_some_time. Defaults is set to time.perf_counter().\n
        time_to_wait (int, optional): How much time do we need to wait before the next request. It is needed into make_request_after_some_time. Defaults is set to 1 second.\n
    Returns:
        tuple: (
            dict: Body of the response received,
            int: Count of requests
        )
    """
    server_request_status_code = 0
    while (
        server_request_status_code != 200
    ):
        if self.is_aborted():
            return None, request_count
        request_count += 1
        try:
            server_request = make_request_after_some_time(
                server=server,
                request_count=request_count,
                logger = logger,
                start_time_to_wait=start_time_to_wait,
                time_to_wait=time_to_wait
            )
            server_request_status_code = server_request.status_code
        except AttributeError:
            pass
    body_content = server_request.json()
    return body_content, request_count