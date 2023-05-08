import pandas as pd
import numpy as np

from utils import add_row

import json
import pprint


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

initial_total_race_time = body_content["onTablo"]["totalRaceTime"]

race_started_button_timestamp = body_content["onTablo"]['raceStartedButtonTimestamp']
race_finished_timestamp = body_content["onTablo"]['raceFinishedTimestamp']

only_one_cycle = 1

teams_stats = body_content["onTablo"]["teams2"]

last_lap_info = {}
for team in teams_stats:
    last_lap_info_update = {
        team: {
            "last_lap": 0,
            "last_kart": 0,
            "current_segment": 1,
            "was_on_pit" : False
        }
    }
    last_lap_info.update(last_lap_info_update)
    
    
df_last_lap_info = pd.DataFrame.from_dict(last_lap_info, orient="index")
last_lap_info = None

while (
    race_started_button_timestamp>race_finished_timestamp
) and not (only_one_cycle == 0):
    if initial_total_race_time != body_content["onTablo"]["totalRaceTime"] or not (only_one_cycle == 0):
        for team in teams_stats:
            lap_count = teams_stats[team]["lapCount"]
            if lap_count !=0:
                pilot_name = teams_stats[team]["pilotName"]
                kart = teams_stats[team]["kart"]
                last_lap_time = teams_stats[team]["lastLap"]
                last_lap_s1_time = teams_stats[team]["lastLapS1"]
                last_lap_s2_time = teams_stats[team]["lastLapS2"]

                if int(kart) == 0 or int(kart) != df_last_lap_info.loc[team, "last_kart"]:
                    true_kart = False
                else: 
                    true_kart = True
                    needed_indexes = df_statistic[
                        (df_statistic.loc[:,"pilot_name"] == pilot_name) 
                        &(df_statistic.loc[:,"true_kart"] == False) 
                        &(
                            (df_statistic.loc[:,"kart"] == 0) |
                            (df_statistic.loc[:,"kart"] ==\
                                df_last_lap_info.loc[str(team), "last_kart"])
                        )
                    ].index
                    df_statistic.loc[needed_indexes, "true_kart"] = True
                    df_statistic.loc[needed_indexes, "kart"] = int(kart)
                    df_last_lap_info.loc[team, "last_kart"] = kart
                
                if int(lap_count) > int(
                    df_last_lap_info.loc[team].at["last_lap"]
                ):
                    add_row.add_a_row(
                        df_statistic,
                        [
                            pilot_name, # pilot_name
                            int(kart), # kart
                            lap_count, 
                            last_lap_time, # lap_time
                            last_lap_s1_time, # s1
                            last_lap_s2_time, # s2
                            df_last_lap_info.loc[team, "current_segment"], #team_segment
                            true_kart, # Flag to check if kart is true or still 0
                        ]
                    )
                    
                    # NEED TO ADD FUNCTIONALITY FOR is_on_pit = True SCENARIO
                    is_on_pit = teams_stats[team]["isOnPit"]
                    if is_on_pit:
                        df_last_lap_info.loc[team, "current_segment"] += 1
                        df_last_lap_info.loc[team, "was_on_pit"] = True
                        
                        
                    
                    
                    df_last_lap_info.loc[team, "last_lap"] = lap_count
                
                best_lap_on_segment = teams_stats[team]["bestLapOnSegment"]
                mid_lap = teams_stats[team]["midLap"]
        
    # RENEW VARIABLES FOR THE NEXT CYCLE
    race_started_button_timestamp = body_content["onTablo"]['raceStartedButtonTimestamp']
    race_finished_timestamp = body_content["onTablo"]['raceFinishedTimestamp']
    
    initial_total_race_time == body_content["onTablo"]["totalRaceTime"]
    
    only_one_cycle -= 1
    # MAKE NEW REQUEST

print(df_statistic)



print(df_statistic)

