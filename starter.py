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

is_debug = 0

teams_stats = body_content["onTablo"]["teams2"]

last_teams_kart = []
for team in teams_stats:
    team_kart = {
        team: 0
    }
    last_teams_kart.append(team_kart)

while (
    race_started_button_timestamp>race_finished_timestamp
) and is_debug == 0:
    if initial_total_race_time != body_content["onTablo"]["totalRaceTime"] or is_debug == 0:
        for team in teams_stats:
            lap_count = teams_stats[str(team)]["lapCount"]
            if lap_count !=0:
                pilot_name = teams_stats[str(team)]["pilotName"]
                kart = teams_stats[str(team)]["kart"]
                last_lap_time = teams_stats[str(team)]["lastLap"]
                last_lap_s1_time = teams_stats[str(team)]["lastLapS1"]
                last_lap_s2_time = teams_stats[str(team)]["lastLapS2"]

                if int(kart) == 0:
                    true_kart = False
                else: 
                    true_kart = True
                
                # NEED TO ADD SOME CHECK OF A LAP COUNTER 
                    # AND/OR CHECKER IF THERE IS A LAP ROW IN THE TABLE
                add_row.add_a_row(
                    df_statistic,
                    [
                        pilot_name, # pilot_name
                        kart, # kart
                        lap_count, 
                        last_lap_time, # lap_time
                        last_lap_s1_time, # s1
                        last_lap_s2_time, # s2
                        true_kart # Flag to check if kart is true or still 0
                    ]
                )
            is_on_pit = teams_stats[str(team)]["isOnPit"]
            best_lap_on_segment = teams_stats[str(team)]["bestLapOnSegment"]
            mid_lap = teams_stats[str(team)]["midLap"]
        
        # RENEW VARIABLES FOR THE NEXT CYCLE
        race_started_button_timestamp = body_content["onTablo"]['raceStartedButtonTimestamp']
        race_finished_timestamp = body_content["onTablo"]['raceFinishedTimestamp']
        
        initial_total_race_time == body_content["onTablo"]["totalRaceTime"]
        
        is_debug += 1
        # MAKE NEW REQUEST

print(df_statistic)
