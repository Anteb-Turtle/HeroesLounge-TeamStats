# -*- coding: utf-8 -*-
"""
MAIN
Set inputs and run to retreive data, calculate stats from the data, and plot the stats
"""

import test_3classes as tc

# =============================================================================
# INPUTS
# =============================================================================
team_name = 'Turtle Team' # enter team complete name
team_tag =  'Turtles' # enter team tag
seasons = [0,1,2] # enter a list of integers: 0 is current season, 1 is past season, ...
# =============================================================================


# =============================================================================
# RETREIVE DATA FROM HEROESLOUNGE.GG
# =============================================================================
## Initialize raw data object
team_data = tc.TeamRawData(team_tag, team_name)
team_data.set_seasons(seasons)

## Import data
team_data.gather_online_data()
#team_data.load_from_json('test.json')

## Store data
team_data.save_to_json()
# =============================================================================


# =============================================================================
# PROCESS DATA
# =============================================================================
team_processed = tc.TeamProcessedData(team_data)
# =============================================================================


# =============================================================================
# STORE DATA IN DATAFRAMES
# =============================================================================
## Convert TeamProcessedData (dictionnaries) to TeamDisplayData (dataframes)
team_display = tc.TeamDisplayData(processed_data = team_processed)

## Store dataframes
team_display.save_to_excel()
# =============================================================================


# =============================================================================
# DISPLAY DATA
# =============================================================================
team_display.display_player_stats(players = 5)
team_display.display_map_stats()
team_display.display_map_bans()
# =============================================================================

