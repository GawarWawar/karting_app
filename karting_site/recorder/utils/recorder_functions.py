import pandas as pd
import numpy as np
import requests
from urllib3 import exceptions

import time

import sys
from os.path import dirname, abspath
import importlib.util
import logging

from recorder import models

def str_lap_or_segment_time_into_float_change(
    lap_time: str
) -> float:
    """Time in data is string and we need to have float. Also, if it is greater then 1 minute, it has format mm:ss:miliseconds, so we are transforming it to seconds.

    Args:
        lap_time (str): Time in format ss.miliseconds or mm:ss:miliseconds as string

    Returns:
        float: Time in seconds as float
    """
    try:
        lap_time = float(lap_time)
    except ValueError:
        split_lap_time = lap_time.split(":")
        lap_time = float(split_lap_time[0])*60+float(split_lap_time[1])
        lap_time = float(f"{lap_time:.2f}")
    return lap_time

def kart_check (
    kart: int,
) -> bool:
    """ Karts are changes by hand, so programme needs to perform a check if kart was changed on valid or it is still 0, and create a flag that indicates this:\n
            yes -> set kart flag to True. It will indicate kart being valid;\n
            no -> set kart flag to False. It will indicate that kart is being not valid. This flag will mark all records with non valid kart, so them could be changed in the future.
    
    Args:
        kart (int): Kart, which shown in the programme.\n
    Returns:
        bool: \n
            True -> indicates kart being valid;\n
            False -> indicates that kart is being not valid. This flag will mark all records with non valid kart, so them could be changed in the future.
    """
    if kart == 0:
       return False
    else: 
       return True


def change_kart_to_true_value(
    current_segment: int,
    race: models.Race,
    team: str,
    kart: int,
    logger: logging.Logger
) -> None:
    """Changes all previous 0 kart records of current segment of the team to valid kart number and set True_kart flag to True in this records;
            make a log about it;

    Args:
        current_segment (int): current segment of the team. Pit stops divide race on the segments, so current segment increases after team`s pit stops;\n
        race (models.Race): instance of a recorder.models.Race, that indicate the race, which is going on;\n
        team (str): team, that we are doing kart change for;\n
        kart (int): true kart, that team is riding on the track right now;\n
        logger (logging.Logger): instance for logger in which we are making logs.\n
    """
    laps_to_change =  models.RaceRecords.objects.filter(
        race = race,
        team_number = int(team),
        true_kart = False,
        team_segment = current_segment,
    )
    
    if laps_to_change:
        changed_laps = []
        for lap in laps_to_change.values('lap_count'):
            changed_laps.append(lap["lap_count"])
        logger.info(f"Records for laps: {changed_laps} was changed for team {team}'s {current_segment} segment to kart {kart}")
        laps_to_change.update(
            true_kart = True,
            kart = kart
        )

def check_name(
    seconds_from_pit: int,
    total_race_time: int,
    pilot_name: str,
    seconds_to_pass:int = 540
) -> bool:
    """ Name of the pilot is changed by hand, so programme needs to check if name was changed. Checking if name is not empty and if team made set amount of time on track after the pit or start, to be sure the name was changed:\n
            yes -> set name flag to True. It will indicate name being valid;\n
            no -> set name flag to False. It will indicate that name is being not valid. This flag will mark all records with non valid name, so them could be changed in the future;

    Args:
        seconds_from_pit (int): Amount of seconds after last pit of the team.\n
        total_race_time (int): Amount of seconds that indicate how many seconds has passed after start of the race.\n
        pilot_name (str): name of the pilot that is now featured in the team`s info.\n
        seconds_to_pass (int, optional): amount of seconds, that needs to pass after the start, for name to become valid. Defaults is set to 540.\n
    
    Returns:
        bool: \n
        True -> indicates name being valid;\n
        False -> indicates that name is being not valid. This flag will mark all records with non valid name, so them could be changed in the future;
    """
    if  (
        seconds_from_pit >= seconds_to_pass 
        and
        total_race_time >= seconds_to_pass
        and not
        pilot_name == ""
    ):
        return True
    else:
        return False

def change_name_to_true_value (
    current_segment: int,
    race: models.Race,
    team: str,
    pilot_name: str,
    logger: logging.Logger,
) -> None:
    """Change pilot name in all previous records of current segment and set the True_name flag to True in them;
            make a log about it;

    Args:
        current_segment (int): current segment of the team. Pit stops divide race on the segments, so current segment increases after team`s pit stops;\n
        race (models.Race): instance of a recorder.models.Race, that indicate the race, which is going on;\n
        team (str): team, that we are doing name change for;\n
        pilot_name (str): true name of the pilot, who is riding on the track right now;\n
        logger (logging.Logger): instance for logger in which we are making logs.\n
    """
    laps_to_change =  models.RaceRecords.objects.filter(
        race = race,
        team_number = int(team),
        true_name = False,
        team_segment = current_segment,
    )
    
    if laps_to_change:
        changed_laps = []
        for lap in laps_to_change.values('lap_count'):
            changed_laps.append(lap["lap_count"])
        logger.info(f"Records for laps: {changed_laps} was changed for team {team}'s {current_segment} segment to name {pilot_name}")
        laps_to_change.update(
            true_name =True,
            pilot_name = pilot_name
        )

    
def make_request_after_some_time(
    server: str,
    request_count: int,
    logger: logging.Logger,
    start_time_to_wait:float = time.perf_counter(),
    time_to_wait: int = 1
) -> tuple:
    """Make request after timer extends over time_to_wait. Returns either requests.Response or None. Make a log about it`s result.

    Args:
        server (str): Link, on which we send a request.\n
        request_count (int): How many times we send request to the server. Need it to include into a log about request result.\n
        logging_file (str): File to write logging info.\n
        start_time_to_wait (float, optional): Timestamp after the last request was done. Defaults is set to time.perf_counter().\n
        time_to_wait (int, optional): How much time do we need to wait before the next request. Defaults is set to 1 second.\n

    Returns:
        requests.Response: response was successful, request.Response will be transferred\n
        None: one of the following exeptions was raised: requests.exceptions.ReadTimeout, ConnectionResetError, exceptions.ProtocolError, requests.exceptions.ConnectionError
    """
    end_time_to_wait = time.perf_counter()
    while end_time_to_wait - start_time_to_wait < time_to_wait:
        end_time_to_wait = time.perf_counter()
    try: 
        server_request = requests.get(
            server, 
            timeout=10
        )
    # If we recieve exeption that indicates that connection wasn`t aquired,
    # we return None to indicate it  
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
    shared_task_instance,
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
        logging_file (str): File to write logging info. It is needed into make_request_after_some_time.\n
        start_time_to_wait (float, optional): Timestamp after the last request was done. It is needed into make_request_after_some_time. Defaults is set to time.perf_counter().\n
        time_to_wait (int, optional): How much time do we need to wait before the next request. It is needed into make_request_after_some_time. Defaults is set to 1 second.\n
    Returns:
        tuple: (
            dict: Body of the response received,
            int: Count of requests
        )
    """
    # We need server_request_status_code to start up cycle
    server_request_status_code = 0
    while (
        server_request_status_code != 200
    ):
        if shared_task_instance.is_aborted():
            return None, request_count
        request_count += 1
        server_request = make_request_after_some_time(
            server=server,
            request_count=request_count,
            logger = logger,
            start_time_to_wait=start_time_to_wait,
            time_to_wait=time_to_wait
        )
        # After make_request_after_some_time returns requests.Response,
        # we can read its status_code and if it indicates about successful response, programme proceed
        # othervie exeption is catched and cycle starts again
        try:
            server_request_status_code = server_request.status_code
        except AttributeError:
            pass
        else:
            logger.info(f"Request numder {request_count} returned {server_request_status_code} status_code ")
        start_time_to_wait = time.perf_counter()
    body_content = server_request.json()
    del start_time_to_wait
    return body_content, request_count