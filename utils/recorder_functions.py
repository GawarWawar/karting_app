import pandas as pd
import numpy as np
import requests

import time

import sys
from os.path import dirname, abspath
import importlib.util

#SCRIPT_DIR = dirname(abspath(__file__))
#path = sys.path.append(dirname(SCRIPT_DIR))

if __name__ == "__main__":
    import add_row
    import tools as u_tools
else:
    spec = importlib.util.spec_from_file_location("add_row", "utils/add_row.py")
    add_row = importlib.util.module_from_spec(spec)
    sys.modules["add_row"] = add_row
    spec.loader.exec_module(add_row)

    spec = importlib.util.spec_from_file_location("u_tools", "utils/tools.py")
    u_tools = importlib.util.module_from_spec(spec)
    sys.modules["add_row"] = u_tools
    spec.loader.exec_module(u_tools)


def kart_check (
    df_statistic: pd.DataFrame,
    df_last_lap_info: pd.DataFrame,
    team: str,
    kart: int,
    pilot_name: str
) -> bool:
    """ Check if kart was changed on valid or it is still 0:
            yes -> changes all previous 0 kart records for this pilot to valid kart number;
            no -> make a flag, to indicate all non valid kard records;
                 + make a last team`s kart = 0.
    
    Args:
        df_statistic (pd.DataFrame): DataFrame with records of laps` statistic.\n
        df_last_lap_info (pd.DataFrame): DataFrame with info about team last state.\n
        team (str): Team, which kart we are cheking.\n
        kart (int): Kart, which shown in the programme.\n
        pilot_name (str): Name of a pilot to look for.\n

    Returns:
        bool: True, if it is valid kart number.\n
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
    total_race_time: int,
    pilot_name: str,
    
    seconds_to_pass:int = 540
) -> bool:
    """Check if team made set amount of time on track after the pit or start:
            yes -> change all names  before this point on the current segment to the current name;
            no -> set a flag to indicate vrong name.

    Args:
        df_statistic (pd.DataFrame): DataFrame with records of laps` statistic.\n
        df_last_lap_info (pd.DataFrame): DataFrame with info about team last state.\n
        team (str): Team that we are checking.\n
        seconds_from_pit (int): Amount of seconds after last pit of the team.\n
        total_race_time (int): Amount of seconds that indicate how many seconds has passed after start of the race.\n
        pilot_name (str): Name of a pilot that we are changing.\n
        seconds_to_pass (int, optional): amount of seconds, that needs to pass after the start, for name to become valid. Defaults is set to 540.\n
    
    Returns:
        bool: True, if set amout of seconds passed after the last pit.
    """
    if  seconds_from_pit >= seconds_to_pass and\
        total_race_time >= seconds_to_pass:
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
            yes -> change team`s flag was_on_pit to true;
            + if it is 1st encounter -> add to segment and renew segment for the team  

    Args:
        is_on_pit (bool): Flag, that indicate if team is on pit.\n
        df_last_lap_info (pd.DataFrame): DataFrame with info about team last state.\n
        team (str): Team, for which we changing it state.\n
    """
    if is_on_pit:
        if df_last_lap_info.loc[team, "was_on_pit"] == False:
            df_last_lap_info.loc[team, "current_segment"] += 1
        df_last_lap_info.loc[team, "was_on_pit"] = True
        
def add_row_with_lap_check(
    df_statistic: pd.DataFrame,
    df_last_lap_info: pd.DataFrame,
    teams_stats: dict,
    team: str,
    true_name: bool,
    true_kart: bool,
    logging_file: str
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
    lap_count = teams_stats[team]["lapCount"]
    if lap_count !=0 and (int(lap_count) > int(
            df_last_lap_info.loc[team].at["last_lap"])):
        
        add_row.add_a_row(
            df_statistic,
            [
                team, #team number in str
                teams_stats[team]["pilotName"], # pilot_name
                int(teams_stats[team]["kart"]), # kart
                lap_count, 
                teams_stats[team]["lastLap"], # lap_time
                teams_stats[team]["lastLapS1"], # s1
                teams_stats[team]["lastLapS2"], # s2
                df_last_lap_info.loc[team, "current_segment"], #team_segment
                true_name, # Flag to check if name is true and was changed after start or pit 
                true_kart, # Flag to check if kart is true or still 0
            ]
        )
        u_tools.write_log_to_file(
            logging_file,
            f"For team {team} added row for lap {lap_count} \n"
        )
        df_last_lap_info.loc[team, "last_lap"] = lap_count
        
def request_was_not_successful_check(
    server_request: requests.Response,
    request_count: int,
    logging_file: str,
    start_time_to_wait:float = time.perf_counter()
) -> tuple:
    """Check, if request was successfully:
            yes -> return body of the response as a first variable;
            no -> try to get valid response every second until valid response;
        As second variable return amount of requests that were needed.

    Args:
        server_request (requests.Response): request we already made to make a check of it status.\n
        request_count (int): How many times we send request.\n
        logging_file (str): File to paste logging info.\n
        start_time_to_wait (float, optional): Timestamp after the last request was done. Defaults is set to time.perf_counter().\n

    Returns:
        tuple: (
            dict: Body of the response received,
            int: Count of requests
        )
    """
    while server_request.status_code != 200:
        end_time_to_wait = time.perf_counter()
        if end_time_to_wait-start_time_to_wait > 1:
            request_count += 1
            server_request = requests.get(
                "https://nfs-stats.herokuapp.com/getmaininfo.json", 
                timeout=10
            )
            u_tools.write_log_to_file(
                logging_file,
                f"Request numder {request_count} took {end_time_to_wait-start_time_to_wait} time to get, after request {request_count-1} failed \n"
            )
            start_time_to_wait = time.perf_counter()
    body_content = server_request.json()
    return body_content, request_count

def make_request_after_some_time  (
    server: str,
    request_count: int,
    logging_file: str,
    start_time_to_wait:float = time.perf_counter(),
    time_to_wait: int = 1
) -> tuple:
    """Check if set amount of time has passed after last request:
            yes -> make new request
            no -> wait for it to pass
        Also make a log about it

    Args:
        server (str): Link, on which we send a request.\n
        request_count (int): How many times we send request to the server.\n
        logging_file (str): File to paste logging info.\n
        start_time_to_wait (float, optional): Timestamp after the last request was done. Defaults is set to time.perf_counter().\n
        time_to_wait (int, optional): How much time do we need to wait before the next request. Defaults is set to 1 second.\n

    Returns:
        tuple: (
            dict: Body of the response received,
            int: Count of requests
        )
    """
    request_count = request_count + 1
    end_time_to_wait = time.perf_counter()
    if end_time_to_wait-start_time_to_wait < time_to_wait:
        while end_time_to_wait-start_time_to_wait < time_to_wait:
            end_time_to_wait = time.perf_counter()
    server_request = requests.get(
        server, 
        timeout=10
    ) 
    u_tools.write_log_to_file(
        logging_file,
        f"Request numder {request_count} took {end_time_to_wait-start_time_to_wait} time to get \n"
    )
    body_content, request_count = request_was_not_successful_check(
        server_request,
        request_count,
        logging_file
    )
    return body_content, request_count