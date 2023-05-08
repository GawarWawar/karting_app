import pandas as pd
import numpy as np

from utils import add_row

import json
import pprint

from utils import tools as u_tools

import time

# TESTING TIMER
start_of_the_programme = time.perf_counter()

# Importing BeautifulSoup class from the bs4 module
from bs4 import BeautifulSoup

# Opening the html file
with open("getmaininfo.json.html", "r") as HTMLFile:
    # Reading the file
    index = HTMLFile.read()
  
# Creating a BeautifulSoup object and specifying the parser
S = BeautifulSoup(index, 'lxml')

body_content = str(S.body.contents[0])
body_content = json.loads(body_content)
#pprint.pprint(body_content)

with open("html.json", "w") as JSONFile:
    json.dump(body_content, JSONFile, indent=2)
    
#body_content = json.dumps(body_content)

df_statistic = pd.read_csv("pilots_stats.csv")

# NEED TO MAKE A FIRST REQUEST HERE

# Flag to check, if totalRaceTime is changing:
    #yes -> starts main cycle functions
    #no -> continue to make requests
initial_total_race_time = body_content["onTablo"]["totalRaceTime"]

# Variables to check if race is still going
race_started_button_timestamp = body_content["onTablo"]['raceStartedButtonTimestamp']
race_finished_timestamp = body_content["onTablo"]['raceFinishedTimestamp']

# Testing variable
only_one_cycle = 2

# Variable to make team_stats calls shorter
teams_stats = body_content["onTablo"]["teams2"]

# Creating dict of teams with info and flags about their past state
last_lap_info = {}
for team in teams_stats:
    last_lap_info_update = {
        team: {
            "last_lap": 0, # info about number of team`s laps
            "last_kart": 0, # info about last team`s cart
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
) \
    and not (only_one_cycle == 0): # TESTING STUFF
    if initial_total_race_time != body_content["onTablo"]["totalRaceTime"]\
        or not (only_one_cycle == 0): # TESTING SUFF
        for team in teams_stats:
            
            # Check if kart was changed on valid or it is still 0:
                #yes -> changes all previous 0 kart records for this pilot to valid kart number
                #no -> make a flag, to indicate all non valid kard records
                    # + make a last team`s kart = 0
            kart = int(teams_stats[team]["kart"])
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
                
            # Check if team made 9 minutes on track after the pit or start:
                #yes -> change all names  before this point on the current segment to the current name
                #no -> set a flag to indicate vrong name 
            if  (int(teams_stats[team]["secondsFromPit"]) >= 540):
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

            # Check is lap_count of the team > then 0 and did it changed:
                #yes -> make a record about last_lap
                    # + renew team`s lap count
                # no -> pass  
            lap_count = teams_stats[team]["lapCount"]
            if lap_count !=0 or (int(lap_count) > int(
                    df_last_lap_info.loc[team].at["last_lap"])):
                pilot_name = teams_stats[team]["pilotName"]
                
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
                
                df_last_lap_info.loc[team, "last_lap"] = lap_count
                   
            # Check if isOnPit flag is True:
                #yes -> change team`s flag was_on_pit to true
                    # + if it is 1st encounter -> add to segment and renew segment for the team  
            is_on_pit = teams_stats[team]["isOnPit"]
            if is_on_pit:
                if df_last_lap_info.loc[team, "was_on_pit"] == False:
                    df_last_lap_info.loc[team, "current_segment"] += 1
                df_last_lap_info.loc[team, "was_on_pit"] = True
            
            # REDUNDENT INFO, NEED TO MAKE A DECISION ABOUT IT
            best_lap_on_segment = teams_stats[team]["bestLapOnSegment"]
            mid_lap = teams_stats[team]["midLap"]
        
    # Renew variables for the next cycle
    race_started_button_timestamp = body_content["onTablo"]['raceStartedButtonTimestamp']
    race_finished_timestamp = body_content["onTablo"]['raceFinishedTimestamp']
    
    initial_total_race_time == body_content["onTablo"]["totalRaceTime"]
    
    # TESTING STUFF
    only_one_cycle -= 1
    
    # CHECK CYCLE TIMING. CYCLE SHOULD NOT BE LOWER THEN n_seconds; 
        # CREATE WAIT CYCLE IF IT NEEDS TO WAIT
    
    # MAKE NEW REQUEST HERE

# TESTING TIMER
end_of_cycle_time = time.perf_counter()
print(df_statistic)

# TESTING TIMER
end_of_programme = time.perf_counter()

# TESTING TIME PRINTS
print(
    "\n",
    "Time to perform preparation before cycle:", prep_to_cycle_finished_time-start_of_the_programme, "\n",
    "Time to perform cycle to run:", (end_of_cycle_time-prep_to_cycle_finished_time), "\n",
    "Time for the whole programme to run:", end_of_programme-start_of_the_programme, "\n",
)
