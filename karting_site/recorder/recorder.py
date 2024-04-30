import pandas as pd
import numpy as np

import json
import requests
import datetime
from dateutil import parser

from celery import current_app, Celery, shared_task
from celery.contrib.abortable import AbortableTask

from . import models
from .utils import recorder_functions

import time
import pprint
import os
import logging
from pathlib import Path

#needed link: https://nfs-stats.herokuapp.com/getmaininfo.json
@shared_task(
    name = "recorder.record_race", 
    bind = True,
    base = AbortableTask
)
def record_race (
    self,
    race_id: int,
) -> None:
    """Creates models.RaceRecords for Race with race_id, that passed as a parametre. Makes requests to https://nfs-stats.herokuapp.com/getmaininfo.json for the needed info and parses it, to genarate models.RaceRecords.
    This is used by Celery, so its marked as @shared_task(name = "recorder.record_race", bind = True, base = AbortableTask)

    Args:
        race_id (int): Id of the race, that models.RaceRecords should be created for
    """
    start_of_the_programme = time.perf_counter()
    server_link = "https://nfs-stats.herokuapp.com/getmaininfo.json"
    
    # Giving race_id outside of the Celery Task
    self.race_id = race_id
    del race_id
    
    # Looking for and writing into variable recorder.models.Race object to 
    # create and change recorder.models.RaceRecords in future steps
    race_instance = models.Race.objects.get(pk = self.race_id)
    
    # Logger set up
    logger_name_and_file_name = f"race_id_{self.race_id}"
    logger = logging.getLogger(logger_name_and_file_name)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    # FileHandler change for logger, to change logger location
    fh = logging.FileHandler(f'recorder/data/logs/{logger_name_and_file_name}.log')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    
    # Testing variable
    only_one_cycle = -1

    # Making first request to retrieve data to start main cycle
    request_count = 0
    body_content, request_count = recorder_functions.make_request_until_its_successful(
        server=server_link,
        request_count=request_count,
        logger=logger,
        time_to_wait = 1,
        shared_task_instance = self
    )
    # Method to abort recording
    if body_content is None:
            recorder_functions.abort_recording(
                race_instance=race_instance,
                logger_instance=logger,
                start_of_the_programme=start_of_the_programme
            )
            return 1

    # Variables to check if race is still going
    race_started_button_timestamp = body_content["onTablo"]['raceStartedButtonTimestamp']
    race_finished_timestamp = body_content["onTablo"]['raceFinishedTimestamp']

    # Gazeting usefull information of the all teams in one variable
    # It will make call of teams` info shorter
    teams_stats = body_content["onTablo"]["teams2"]

    # Creating default dict of teams with info and flags about their past state.
    # Dict is created to fit all possible teams, even if they are not in the race.
    # Most possible teams number are listed under body_content["onTablo"]["karts"].
    # In sircumstances of the rent karting, team number indicates just a kart number,
    # however during Big races this indicates team number and karts are managed by hands.
    # That is why body_content["onTablo"]["karts"] has all possible team numbers
    last_lap_info = {}
    teams = body_content["onTablo"]["karts"]
    teams.append(88)
    for team in teams:
        last_lap_info_update = {
            str(team): {
                # info about number of team`s laps
                "last_lap": 0, 
                # info about last team`s kart
                "last_kart": 0, 
                # segment that team is doing. It will be renewd
                "current_segment": 1,
                # flag to separate segments and make sure the right pilot name is adding 
                "was_on_pit" : True 
            }
        }
        last_lap_info.update(last_lap_info_update)
    del teams

    # If recorder was reopened mid race,
    # current_segment should be set accrate to each team`s current segment 
    for team in teams_stats:
        last_lap_info[team]["current_segment"] = len(teams_stats[team]["segments"])
        
    df_last_lap_info = pd.DataFrame.from_dict(last_lap_info, orient="index")
    last_lap_info = None

    # End of preparation before main cycle
    preparation_ends = time.perf_counter()
    logger.info(f"Time of preparation: {preparation_ends-start_of_the_programme}")

    # Cycle to check, if totalRaceTime is changing:
        #no -> make new requests
        #yes -> Finish making requestss and proceed with main cycle
    total_race_time = body_content["onTablo"]["totalRaceTime"]

    while (
            total_race_time == body_content["onTablo"]["totalRaceTime"] 
    ):
        # BUG HAVE BEEN FOUND HERE
        # TODO: NEED TO FIX THE TIMING IN WHICH FUNCTION MAKES REQUESTS, RN IT DOES NOT RESET start_time_to_wait
        body_content, request_count = recorder_functions.make_request_until_its_successful(
            server=server_link,
            request_count=request_count,
            logger=logger,
            shared_task_instance = self,
            start_time_to_wait = time.perf_counter() # attempt to fix, check is needed
        )
        if body_content is None:
            recorder_functions.abort_recording(
                race_instance=race_instance,
                logger_instance=logger,
                start_of_the_programme=start_of_the_programme
            )
            return 1

    # Main cycle
    while (
        # In the end of the race race_finished_timestamp will become bigger and cycle will end
        (
            race_started_button_timestamp > race_finished_timestamp
        )
    ) and not (
        only_one_cycle == 0 # Check used while testing
    ): 
        cycle_start_time = time.perf_counter()
        for team in teams_stats:
            pilot_name = teams_stats[team]["pilotName"]
            
            float_total_time_of_the_race = parser.isoparse("2001-04-07," + total_race_time)
            float_total_time_of_the_race = float_total_time_of_the_race.hour*3600+float_total_time_of_the_race.minute*60+float_total_time_of_the_race.second
            true_name = recorder_functions.check_name(
                seconds_from_pit=int(teams_stats[team]["secondsFromPit"]),
                total_race_time=float_total_time_of_the_race,
                pilot_name=pilot_name
            )
            
            # Check if team is on PitStip:
            #   yes -> change team`s flag was_on_pit to true and renew segment for the team;
            is_on_pit=teams_stats[team]["isOnPit"]
            if is_on_pit:
                df_last_lap_info.loc[team, "was_on_pit"] = True
                df_last_lap_info.loc[team, "current_segment"] = len(teams_stats[team]["segments"])
        
            # Check that initiates name change
            if (
                df_last_lap_info.loc[team, "was_on_pit"]
                and
                true_name
                and not
                is_on_pit
            ):
                recorder_functions.change_name_to_true_value(
                    current_segment=df_last_lap_info.loc[team, "current_segment"],
                    race=race_instance,
                    team=team,
                    pilot_name=pilot_name,
                    logger=logger,
                )
                df_last_lap_info.loc[team, "was_on_pit"] = False
            
            kart = int(teams_stats[team]["kart"])
            true_kart = recorder_functions.kart_check(
                kart=kart,
            )
            
            # Check that initiates kart change
            if (
                true_kart
                and
                kart != df_last_lap_info.loc[team, "last_kart"]
            ):
                recorder_functions.change_kart_to_true_value(
                    current_segment=df_last_lap_info.loc[team, "current_segment"],
                    race=race_instance,
                    team=team,
                    kart=kart,
                    logger=logger
                )
                    
            # Renew last_kart after all kart checks and changes 
            df_last_lap_info.loc[team, "last_kart"] = kart
            
            # Check if team made a new lap that initiates creation of lap record 
            lap_count = teams_stats[team]["lapCount"]
            if (
                lap_count !=0 
                and 
                (
                    int(lap_count) 
                    > 
                    int(
                        df_last_lap_info.loc[team].at["last_lap"]
                    )
                )
            ):
                teams_stats[team]["lastLap"] = recorder_functions.str_lap_or_segment_time_into_float_change(
                    teams_stats[team]["lastLap"]
                )
                teams_stats[team]["lastLapS1"] = recorder_functions.str_lap_or_segment_time_into_float_change(
                    teams_stats[team]["lastLapS1"]
                )
                teams_stats[team]["lastLapS2"] = recorder_functions.str_lap_or_segment_time_into_float_change(
                    teams_stats[team]["lastLapS2"]
                )

                lap_record = models.RaceRecords.objects.create(
                    # Using race object created earlier
                    race = race_instance,
                    team_number = int(team),
                    pilot_name = pilot_name,
                    kart = kart,
                    # Times are in float format after the change
                    lap_count = teams_stats[team]["lapCount"],
                    lap_time = teams_stats[team]["lastLap"],
                    s1_time = teams_stats[team]["lastLapS1"],
                    s2_time = teams_stats[team]["lastLapS2"],
                    
                    team_segment = df_last_lap_info.loc[team, "current_segment"],
                    
                    true_name = true_name,
                    true_kart = true_kart,
                )
                lap_record.save()
                
                logger.info(f"For team {team} added row for lap {lap_count}")           
                df_last_lap_info.loc[team, "last_lap"] = lap_count
        
        # New request
        body_content, request_count = recorder_functions.make_request_until_its_successful(
            server=server_link,
            request_count=request_count,
            logger=logger,
            start_time_to_wait=cycle_start_time,
            shared_task_instance = self
        )
        if body_content is None:
            recorder_functions.abort_recording(
                race_instance=race_instance,
                logger_instance=logger,
                start_of_the_programme=start_of_the_programme
            )
            return 1
        
        # Renew variables for the next cycle
        race_started_button_timestamp = body_content["onTablo"]['raceStartedButtonTimestamp']
        race_finished_timestamp = body_content["onTablo"]['raceFinishedTimestamp']
        total_race_time = body_content["onTablo"]["totalRaceTime"]
        teams_stats = body_content["onTablo"]["teams2"]
        
        end_of_the_cycle = time.perf_counter()
        logger.info(f"Time of cycle: {end_of_the_cycle-cycle_start_time}, after request {request_count}")

        # TESTING STUFF
        only_one_cycle -= 0

    race_instance.was_recorded_complete = True
    race_instance.save()
    
    # End of the programme
    end_of_programme = time.perf_counter()
    logger.info(f"Amount of time programme took to run: {end_of_programme-start_of_the_programme}")
    
    return 0