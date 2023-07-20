import pandas as pd
import numpy as np

import json
import requests
import datetime
from dateutil import parser

from celery import current_app, Celery, shared_task
from celery.contrib.abortable import AbortableTask

from . import models
from .utils import add_row
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
):
    self.race_id = race_id
    
    # Logger set up
    logger_name_and_file_name = f"race_id_{race_id}_{datetime.datetime.now()}"
    logger = logging.getLogger(logger_name_and_file_name)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # FileHandler
    fh = logging.FileHandler(f'recorder/data/logs/{logger_name_and_file_name}.log')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    
    
    # Testing variable
    only_one_cycle = -1

    # Start of the program time
    start_of_the_programme = time.perf_counter()

    # Reseting main DataFrame: clearing data, leaving only structure with needed columns
    df_statistic = pd.DataFrame(
        {
            "team": pd.Series(int),
            "pilot": pd.Series(str),
            "kart": pd.Series(int),
            "lap": pd.Series(int),
            "lap_time": pd.Series(float),
            "s1": pd.Series(float),
            "s2": pd.Series(float),
            "segment": pd.Series(int),
            "true_name": pd.Series(bool),
            "true_kart": pd.Series(bool)
        }
    )
    df_statistic = df_statistic.drop(0)

    # Making first request
    request_count = 0
    body_content, request_count = recorder_functions.make_request_until_its_successful(
        server="https://nfs-stats.herokuapp.com/getmaininfo.json",
        request_count=request_count,
        logger=logger,
        time_to_wait = 0,
        self = self
    )
    if body_content == None:
            logger.info(f"Recording stopped at {datetime.datetime.now()}")
            return

    # Flag to check, if totalRaceTime is changing:
        #yes -> starts main cycle functions
        #no -> continue to make requests
    initial_total_race_time = body_content["onTablo"]["totalRaceTime"]
    race_started = False

    # Variables to check if race is still going
    race_started_button_timestamp = body_content["onTablo"]['raceStartedButtonTimestamp']
    race_finished_timestamp = body_content["onTablo"]['raceFinishedTimestamp']

    # Variable to make team_stats calls shorter
    teams_stats = body_content["onTablo"]["teams2"]

    # Creating default dict of teams with info and flags about their past state
    last_lap_info = {}
    teams = body_content["onTablo"]["karts"]
    teams.append(88)
    for team in teams:
        last_lap_info_update = {
            str(team): {
                "last_lap": 0, # info about number of team`s laps
                "last_kart": 0, # info about last team`s kart
                "current_segment": 1, # segment that team is doing
                "was_on_pit" : True # flag to separate segments and make sure the right pilot name is adding
            }
        }
        last_lap_info.update(last_lap_info_update)

    for team in teams_stats:
        last_lap_info[team]["current_segment"] = len(teams_stats[team]["segments"])
        
    df_last_lap_info = pd.DataFrame.from_dict(last_lap_info, orient="index")
    last_lap_info = None

    # End of preparation before main cycle
    preparation_ends = time.perf_counter()
    logger.info(f"Time of preparation: {preparation_ends-start_of_the_programme}")

    # Main cycle
    while (
        # In the end of the race race_finished_timestamp will become bigger and cycle will end
        (
            race_started_button_timestamp > race_finished_timestamp
        )
        or
        (
            initial_total_race_time == body_content["onTablo"]["totalRaceTime"] 
            and not 
            race_started
        ) 
    ) and not (
        only_one_cycle == 0 # TESTING STUFF
    ): 
        cycle_start_time = time.perf_counter()
        for team in teams_stats:
            pilot_name = teams_stats[team]["pilotName"]
            
            time_of_the_race = parser.isoparse("2001-04-07,"+body_content["onTablo"]["totalRaceTime"])
            time_of_the_race = time_of_the_race.hour*3600+time_of_the_race.minute*60+time_of_the_race.second
            true_name = recorder_functions.set_name_flag_after_check_time_after_pit(
                seconds_from_pit=int(teams_stats[team]["secondsFromPit"]),
                total_race_time=time_of_the_race
            )
            
            is_on_pit=teams_stats[team]["isOnPit"]
            recorder_functions.set_was_on_pit_and_current_segment(
                is_on_pit=is_on_pit,
                df_last_lap_info=df_last_lap_info,
                team=team,
                teams_segment_count=len(teams_stats[team]["segments"])
            )
            
            recorder_functions.change_name_to_true_name_after_the_pit(
                df_statistic=df_statistic,
                df_last_lap_info=df_last_lap_info,
                team=team,
                pilot_name=pilot_name,
                logger=logger,
                true_name=true_name,
                is_on_pit=is_on_pit
            )
            
            if (
                df_last_lap_info.loc[team, "was_on_pit"] == True
                and
                true_name
                and not
                is_on_pit
            ):
                laps_to_change =  models.Race.objects.filter(
                    race = race_id,
                    team_number = int(team),
                    true_name = False,
                    team_segment = df_last_lap_info.loc[team, "current_segment"],
                )
                
                if laps_to_change:
                    laps_to_change.true_name = True
                    laps_to_change.pilot_name = pilot_name
                    laps_to_change.update()
            
            kart = int(teams_stats[team]["kart"])
            true_kart = recorder_functions.kart_check(
                df_last_lap_info=df_last_lap_info,
                team=team,
                kart=kart,
            )
                
            if (
                true_kart
                and
                kart != df_last_lap_info.loc[team, "last_kart"]
            ):
                race = models.Race.objects.get(pk = race_id)
                laps_to_change =  models.RaceRecords.objects.filter(
                    race = race,
                    team_number = int(team),
                    true_kart = False,
                    team_segment = df_last_lap_info.loc[team, "current_segment"],
                )
                
                if laps_to_change:
                    laps_to_change.true_kart = True
                    laps_to_change.kart = kart
                    laps_to_change.update()
                    
            
            recorder_functions.change_kart_on_true_value(
                df_statistic=df_statistic,
                df_last_lap_info=df_last_lap_info,
                team=team,
                kart=kart,
                logger=logger
            )
            
            lap_count = teams_stats[team]["lapCount"]
            if lap_count !=0 and (int(lap_count) > int(
                df_last_lap_info.loc[team].at["last_lap"])):
                teams_stats[team]["lastLap"] = recorder_functions.str_lap_time_into_float_change(
                    teams_stats[team]["lastLap"]
                )
                teams_stats[team]["lastLapS1"] = recorder_functions.str_lap_time_into_float_change(
                    teams_stats[team]["lastLapS1"]
                )
                teams_stats[team]["lastLapS2"] = recorder_functions.str_lap_time_into_float_change(
                    teams_stats[team]["lastLapS2"]
                )
                
                recorder_functions.add_lap_as_a_row(
                    df_statistic=df_statistic,
                    df_last_lap_info=df_last_lap_info,
                    teams_stats=teams_stats,
                    team=team,
                    true_name=true_name,
                    true_kart=true_kart,
                )
                
                race = models.Race.objects.get(pk=race_id)
                lap_record = models.RaceRecords.objects.create(
                    race = race,
                    team_number = int(team),
                    pilot_name = pilot_name,
                    kart = int(teams_stats[team]["kart"]),
                    lap_count = teams_stats[team]["lapCount"],
                    lap_time = teams_stats[team]["lastLap"],
                    s1_time = teams_stats[team]["lastLapS1"],
                    s2_time = teams_stats[team]["lastLapS2"],
                    team_segment = df_last_lap_info.loc[team, "current_segment"],
                    true_name = true_name,
                    true_kart = true_kart,
                )
                logger.info(lap_record)
                lap_record.save()
                     
                logger.info(f"For team {team} added row for lap {lap_count}")           
                df_last_lap_info.loc[team, "last_lap"] = lap_count
        
        # New request
        body_content, request_count = recorder_functions.make_request_until_its_successful(
            server="https://nfs-stats.herokuapp.com/getmaininfo.json",
            request_count=request_count,
            logger=logger,
            start_time_to_wait=cycle_start_time,
            self = self
        )
        if body_content == None:
            logger.info(f"Recording stopped at {datetime.datetime.now()}")
            return
        
        # Renew variables for the next cycle
        race_started_button_timestamp = body_content["onTablo"]['raceStartedButtonTimestamp']
        race_finished_timestamp = body_content["onTablo"]['raceFinishedTimestamp']
        
        initial_total_race_time == body_content["onTablo"]["totalRaceTime"]
        teams_stats = body_content["onTablo"]["teams2"]
        
        race_started = True
        
        end_of_the_cycle = time.perf_counter()
        logger.info(f"Time of cycle: {end_of_the_cycle-cycle_start_time}, after request {request_count}")
        
        # TESTING STUFF
        only_one_cycle -= 1

    # End of the programme
    end_of_programme = time.perf_counter()
    logger.info(f"Amount of time programme took to run: {end_of_programme-start_of_the_programme}")