import pandas as pd
import numpy as np

import json
import requests

from utils import add_row
from utils import main_functions
from utils import tools as u_tools

import time
import pprint

#needed link: https://nfs-stats.herokuapp.com/getmaininfo.json

# TESTING TIMER
start_of_the_programme = time.perf_counter()

request_count = 0

# # Importing BeautifulSoup class from the bs4 module
# from bs4 import BeautifulSoup

# # Opening the html file
# with open("getmaininfo.json.html", "r") as HTMLFile:
#     # Reading the file
#     index = HTMLFile.read()
  
# # Creating a BeautifulSoup object and specifying the parser
# S = BeautifulSoup(index, 'lxml')

# body_content = str(S.body.contents[0])
# body_content = json.loads(body_content)

# with open("html.json", "w") as JSONFile:
#     json.dump(body_content, JSONFile, indent=2)


body_content = main_functions(
    "https://nfs-stats.herokuapp.com/getmaininfo.json"    
)

df_statistic = pd.read_csv("pilots_stats.csv")

# Flag to check, if totalRaceTime is changing:
    #yes -> starts main cycle functions
    #no -> continue to make requests
initial_total_race_time = body_content["onTablo"]["totalRaceTime"]

# Variables to check if race is still going
race_started_button_timestamp = body_content["onTablo"]['raceStartedButtonTimestamp']
race_finished_timestamp = body_content["onTablo"]['raceFinishedTimestamp']

# Testing variable
only_one_cycle = -1

# Variable to make team_stats calls shorter
teams_stats = body_content["onTablo"]["teams2"]

# Creating default dict of teams with info and flags about their past state
last_lap_info = {}
for team in body_content["onTablo"]["karts"]:
    last_lap_info_update = {
        team: {
            "last_lap": 0, # info about number of team`s laps
            "last_kart": 0, # info about last team`s kart
            "current_segment": 1, # segment that team is doing
            "was_on_pit" : True # flag to separate segments and make sure the right pilot name is adding
        }
    }
    last_lap_info.update(last_lap_info_update)
    
df_last_lap_info = pd.DataFrame.from_dict(last_lap_info, orient="index")
last_lap_info = None

# TESTING TIMER
prep_to_cycle_finished_time = time.perf_counter()

# Main cycle
while (
    # In the end of the race race_finished_timestamp will become bigger and cycle will end
    race_started_button_timestamp > race_finished_timestamp
) and not (only_one_cycle == 0): # TESTING STUFF
    start_time_to_wait = time.perf_counter()
    if initial_total_race_time != body_content["onTablo"]["totalRaceTime"]\
        or not (only_one_cycle == 0): # TESTING SUFF
        
        for team in teams_stats:
            pilot_name = teams_stats[team]["pilotName"]
                
            # Check if team made 9 minutes on track after the pit or start:
                #yes -> change all names  before this point on the current segment to the current name
                #no -> set a flag to indicate vrong name 
            seconds_from_pit = int(teams_stats[team]["secondsFromPit"])
            true_name = main_functions.name_check_after_pit(
                df_statistic,
                df_last_lap_info,
                team,
                seconds_from_pit,
                pilot_name
            )

            # Check if kart was changed on valid or it is still 0:
                #yes -> changes all previous 0 kart records for this pilot to valid kart number
                #no -> make a flag, to indicate all non valid kard records
                    # + make a last team`s kart = 0
            kart = int(teams_stats[team]["kart"])
            true_kart = main_functions.kart_check(
                df_statistic,
                df_last_lap_info,
                team,
                kart,
                pilot_name
            )

            # Check is lap_count of the team > then 0 and did it changed:
                #yes -> make a record about last_lap
                    # + renew team`s lap count
                # no -> pass  
            lap_count = teams_stats[team]["lapCount"]
            if lap_count !=0 and (int(lap_count) > int(
                    df_last_lap_info.loc[team].at["last_lap"])):
                
                add_row.add_a_row(
                    df_statistic,
                    [
                        team, #team number in str
                        pilot_name, # pilot_name
                        kart, # kart
                        lap_count, 
                        teams_stats[team]["lastLap"], # lap_time
                        teams_stats[team]["lastLapS1"], # s1
                        teams_stats[team]["lastLapS2"], # s2
                        df_last_lap_info.loc[team, "current_segment"], #team_segment
                        true_name, # Flag to check if name is true and was changed after start or pit 
                        true_kart, # Flag to check if kart is true or still 0
                    ]
                )
                print("Row_added for team:", team)
                
                df_last_lap_info.loc[team, "last_lap"] = lap_count
                   
            # Check if isOnPit flag is True:
                #yes -> change team`s flag was_on_pit to true
                    # + if it is 1st encounter -> add to segment and renew segment for the team  
            is_on_pit = teams_stats[team]["isOnPit"]
            main_functions.check_is_team_on_pit(
                is_on_pit,
                df_last_lap_info,
                team
            )
            
            # REDUNDENT INFO, NEED TO MAKE A DECISION ABOUT IT
            best_lap_on_segment = teams_stats[team]["bestLapOnSegment"]
            mid_lap = teams_stats[team]["midLap"]
    
    # TESTING STUFF
    only_one_cycle -= 1
    
    # CHECK CYCLE TIMING. CYCLE SHOULD NOT BE LOWER THEN n_seconds; 
        # CREATE WAIT CYCLE IF IT NEEDS TO WAIT
    
    df_statistic.to_csv("test_data.csv", index=False, index_label=False)
    
    # MAKE NEW REQUEST HERE
    body_content = main_functions.new_request(
        start_time_to_wait,
        request_count
    )
    
    # Renew variables for the next cycle
    race_started_button_timestamp = body_content["onTablo"]['raceStartedButtonTimestamp']
    race_finished_timestamp = body_content["onTablo"]['raceFinishedTimestamp']
    
    initial_total_race_time == body_content["onTablo"]["totalRaceTime"]
    teams_stats = body_content["onTablo"]["teams2"]

    


# TESTING TIMER
end_of_cycle_time = time.perf_counter()
print(df_statistic)

# TESTING TIMER
end_of_programme = time.perf_counter()

#TESTING TIME PRINTS
print(
    "\n",
    "Time to perform preparation before cycle:", prep_to_cycle_finished_time-start_of_the_programme, "\n",
    "Time to perform cycle to run:", (end_of_cycle_time-prep_to_cycle_finished_time), "\n",
    "Time for the whole programme to run:", end_of_programme-start_of_the_programme, "\n",
)

