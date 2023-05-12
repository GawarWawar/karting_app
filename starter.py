import pandas as pd
import numpy as np

import json
import requests
import datetime

from utils import add_row
from utils import main_functions
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
body_content, request_count = main_functions.make_request_after_some_time(
    "https://nfs-stats.herokuapp.com/getmaininfo.json",
    request_count,
    0,
    0
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
for team in body_content["onTablo"]["karts"]:
    last_lap_info_update = {
        str(team): {
            "last_lap": 0, # info about number of team`s laps
            "last_kart": 0, # info about last team`s kart
            "current_segment": 1, # segment that team is doing
            "was_on_pit" : True # flag to separate segments and make sure the right pilot name is adding
        }
    }
    last_lap_info.update(last_lap_info_update)
    
df_last_lap_info = pd.DataFrame.from_dict(last_lap_info, orient="index")
last_lap_info = None

# End of preparation before main cycle
preparation_ends = time.perf_counter()
u_tools.write_log_to_file(
    path_to_logging_file,
    f"Time of preparation: {preparation_ends-start_of_the_programme} \n"
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
    #NEED TO REDO CYCLE START. RN IT DOESNT WORK AS INTENDED
) and not (only_one_cycle == 0): # TESTING STUFF
    start_of_the_cycle = time.perf_counter()
    start_time_to_wait = time.perf_counter()
    for team in teams_stats:
        pilot_name = teams_stats[team]["pilotName"]
            
        # Check if team made 9 minutes on track after the pit or start:
            #yes -> change all names  before this point on the current segment to the current name
            #no -> set a flag to indicate vrong name 
        true_name = main_functions.name_check_after_pit(
            df_statistic,
            df_last_lap_info,
            team,
            int(teams_stats[team]["secondsFromPit"]),
            pilot_name
        )
        # Check if kart was changed on valid or it is still 0:
            #yes -> changes all previous 0 kart records for this pilot to valid kart number
            #no -> make a flag, to indicate all non valid kard records
                # + make a last team`s kart = 0
        true_kart = main_functions.kart_check(
            df_statistic,
            df_last_lap_info,
            team,
            int(teams_stats[team]["kart"]),
            pilot_name
        )
        # Check is lap_count of the team > then 0 and did it changed:
            #yes -> make a record about last_lap
                # + renew team`s lap count
            # no -> pass  
        main_functions.add_row_with_lap_check(
            df_statistic,
            df_last_lap_info,
            teams_stats,
            team,
            true_name,
            true_kart
        )
               
        # Check if isOnPit flag is True:
            #yes -> change team`s flag was_on_pit to true
                # + if it is 1st encounter -> add to segment and renew segment for the team  
        main_functions.check_is_team_on_pit(
            teams_stats[team]["isOnPit"],
            df_last_lap_info,
            team
        )
    
    # Writing gazered statistic into the file
    df_statistic.to_csv(
        path_to_records_file, 
        index=False, 
        index_label=False)
    
    # New request
    body_content, request_count = main_functions.make_request_after_some_time(
        "https://nfs-stats.herokuapp.com/getmaininfo.json",
        request_count,
        start_time_to_wait,
    )
    
    # Renew variables for the next cycle
    race_started_button_timestamp = body_content["onTablo"]['raceStartedButtonTimestamp']
    race_finished_timestamp = body_content["onTablo"]['raceFinishedTimestamp']
    
    initial_total_race_time == body_content["onTablo"]["totalRaceTime"]
    teams_stats = body_content["onTablo"]["teams2"]
    
    race_started = True
    
    end_of_the_cycle = time.perf_counter()
    u_tools.write_log_to_file(
        path_to_logging_file,
        f"Time of cycle: {end_of_the_cycle-start_of_the_cycle}, after request {request_count} \n"
    )
    
    # TESTING STUFF
    only_one_cycle -= 1

# End of the programme
end_of_programme = time.perf_counter()
u_tools.write_log_to_file(
        path_to_logging_file,
        f"Amount of time programme took to run: {end_of_programme -start_of_the_programme} \n"
    )

