import pandas as pd
import numpy as np

import json
import requests
import datetime
from dateutil import parser

from utils import add_row
from utils import recorder_functions
from utils import tools as u_tools

import time
import pprint

#needed link: https://nfs-stats.herokuapp.com/getmaininfo.json

# Testing variable
only_one_cycle = -1

# Start of the program time
start_of_the_programme = time.perf_counter()

# Adding file pathes and names to write our record and logs for this run
exact_date_and_time = str(datetime.datetime.now())
logging_file_name = exact_date_and_time + ".txt"
record_file_name = exact_date_and_time + ".csv"
path_to_logging_file = "data/logs/" + logging_file_name
path_to_records_file = "data/records/" + record_file_name

u_tools.create_file(path_to_logging_file)
u_tools.create_file(path_to_records_file)

# Reseting main DataFrame: clearing data, leaving only structure with needed columns
df_statistic = pd.read_csv("pilots_stats_template.csv")

# Making first request
request_count = 0
body_content, request_count = recorder_functions.make_request_after_some_time(
    server="https://nfs-stats.herokuapp.com/getmaininfo.json",
    request_count=request_count,
    logging_file=path_to_logging_file,
    time_to_wait = 0
)

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
u_tools.write_log_to_file(
    logging_file_path=path_to_logging_file,
    log_to_add=f"Time of preparation: {preparation_ends-start_of_the_programme} \n"
)

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
) and not (only_one_cycle == 0): # TESTING STUFF
    start_of_the_cycle = time.perf_counter()
    start_time_to_wait = time.perf_counter()
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
            logging_file=path_to_logging_file,
            true_name=true_name,
            is_on_pit=is_on_pit
        )
        
        true_kart = recorder_functions.kart_check(
            df_statistic=df_statistic,
            df_last_lap_info=df_last_lap_info,
            team=team,
            kart=int(teams_stats[team]["kart"]),
            logging_file=path_to_logging_file
        )
        
        recorder_functions.add_row_with_lap_check(
            df_statistic=df_statistic,
            df_last_lap_info=df_last_lap_info,
            teams_stats=teams_stats,
            team=team,
            true_name=true_name,
            true_kart=true_kart,
            logging_file=path_to_logging_file    
        )
    
    # Writing gazered statistic into the file
    df_statistic.to_csv(
        path_to_records_file, 
        index=False, 
        index_label=False)
    
    # New request
    body_content, request_count = recorder_functions.make_request_after_some_time(
        server="https://nfs-stats.herokuapp.com/getmaininfo.json",
        request_count=request_count,
        logging_file=path_to_logging_file,
        start_time_to_wait=start_time_to_wait,
    )
    
    # Renew variables for the next cycle
    race_started_button_timestamp = body_content["onTablo"]['raceStartedButtonTimestamp']
    race_finished_timestamp = body_content["onTablo"]['raceFinishedTimestamp']
    
    initial_total_race_time == body_content["onTablo"]["totalRaceTime"]
    teams_stats = body_content["onTablo"]["teams2"]
    
    race_started = True
    
    end_of_the_cycle = time.perf_counter()
    u_tools.write_log_to_file(
        logging_file_path=path_to_logging_file,
        log_to_add=f"Time of cycle: {end_of_the_cycle-start_of_the_cycle}, after request {request_count} \n"
    )
    
    # TESTING STUFF
    only_one_cycle -= 1

# End of the programme
end_of_programme = time.perf_counter()
u_tools.write_log_to_file(
    logging_file_path=path_to_logging_file,
    log_to_add=f"Amount of time programme took to run: {end_of_programme-start_of_the_programme} \n",
)

