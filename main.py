# -*- coding: utf-8 -*-
"""
MAIN
Set inputs and run to retreive data, calculate stats from the data, and plot the stats
"""

# =============================================================================
# DOC
# =============================================================================

import json
import pandas as pd
import requests
from bs4 import BeautifulSoup as soup
from matplotlib import pyplot as plt
import supportfunctions as fun
import formatdata as fd

# =============================================================================
# INPUTS
# =============================================================================
team_shortname = 'JTFM' # enter team name abbreviation
team_longname = 'Jaina The Frost Mage' # enter full name of the team
list_of_last_seasons = [1, 2, 3] # list of integers: 0 is current season, 1 is past season, ...
plot_results = 'yes' # 'yes' to show bar plots of statistics
save_json = 'yes' # 'yes' to save data gathered to json
save_excel =  'yes' # 'yes' to save formated data to excel
#==============================================================================


# =============================================================================
# RETREIVE DATA FROM HEROESLOUNGE.GG
# =============================================================================
print('Requesting team html')
url = "https://heroeslounge.gg/team/view/"+team_shortname
r = requests.get(url)
result = requests.get(url)
page = result.text
doc = soup(page, "html5")
print('Request completed')
print('\n')

# =============================================================================
## Retreive seasons list
id_list = [element.get('id') for element in doc.find_all('div')]
ids = [i for i in id_list if 'roundmatches' in str(i)]
## Filter by season
ids = ids[1:]
ids = [ids[i] for i in list_of_last_seasons]

# =============================================================================
## Find all matches links in filtered seasons
matches_links = []
for id1 in ids:
    for div in doc.find_all('div', {'id': id1}):
        matches_list = div.find_all('a')
    matches_list = matches_list[1::3]

    matches_links = matches_links+[str(i.get('href')) for i in matches_list]

print(matches_links)
print('\n')

# =============================================================================
## Retreive data from each match
matchs_data = []
match_picks = []
for link in matches_links:
    print('Requesting link:', link)
    result1 = requests.get(link)
    print('Request completed')
    page1 = result1.text
    doc1 = soup(page1, "html5")
    games = doc1.find_all('div', {'class': 'tab-pane'})
    games_id = [i.get('id') for i in games]

    ## In case there is a forfeit ##
    if (True in [True for g in games if 'No Replay File found!' in g.text]):
        print(games_id, ' no replay files found')
        continue
    ## ##

    ## Extract data from each game/round of the match
    round_data = []
    round_picks_team1 = []
    round_picks_team2 = []
    round_bans_team1 = []
    round_bans_team2 = []
    for game in games:
        heroes = [element.get('alt') for element in game.find_all('img')]
        team1 = heroes[0]
        team2 = heroes[1]
        teams = [team1, team2]
        heroes = heroes[2:19]
        picks = heroes[0:10]
        bans_team1 = heroes[10:13]
        bans_team2 = heroes[14:17]
        players = [element.text for element in game.find_all('a')]
        players = players[2:12]
        players = [' '.join(p.split()) for p in players]

        picks_team1 = dict(zip(players[0:5], picks[0:5]))
        picks_team2 = dict(zip(players[5:10], picks[5:10]))
        round_picks_team1.append(picks_team1)
        round_picks_team2.append(picks_team2)

        round_bans_team1.append(bans_team1)
        round_bans_team2.append(bans_team2)


    print('Match data gathered')

    duration = doc1.find_all('div', {'class':"col-12 col-md-2"})
    duration = [d.text.split()[1] for d in duration]

    maps = doc1.find_all('span', {'class':"badge badge-info"})
    maps_played = [m.text for m in maps]

    winner = doc1.findAll('span', {'class':["badge badge-success float-left", "badge badge-success float-right"]})
    winner = [team1 if w.get('class')[2] == "float-right" else team2 for w in winner]

    ## Store all data in a dictionnary
    match_data = {'match': link.split('/')[-1], 'games_id': games_id, 'teams': teams, \
        'picks_team_1': round_picks_team1, 'picks_team_2': round_picks_team2, \
        'bans_team_1': round_bans_team1, 'bans_team_2': round_bans_team2, 'durations': duration, \
        'maps': maps_played, 'winners': winner}
    matchs_data.append(match_data)

print('---- All data gathered ----')


## Save to JSON
if save_json == 'yes':
    with open(team_shortname+'_data.json', 'w') as file:
        json.dump(match_data, file)


# =============================================================================




# =============================================================================
# FORMAT DATA
# =============================================================================

# =============================================================================
## Total WR

## Total and Map winrate
map_list, map_uni = fd.get_maplist(matchs_data)
results = fd.get_results(match_data, team_longname)
team_winrate = fd.get_global_winrate(matchs_data, team_longname)
print(team_longname, ' total winrate over chosen seasons: \n', team_winrate, '%\n')

## Map WR
map_wr, map_w, map_p = fd.get_map_winrate(map_list, map_uni, results)

winrate_bymap = dict(zip(map_uni, map_wr))
print('Winrate by map :\n', winrate_bymap, '\n')
number_bymap = dict(zip(map_uni, map_p))
print('Number of times map played :\n', number_bymap, '\n')

# =============================================================================
## Heroes played by player and WR

## get list of picked heroes
picks = fd.get_picks(matchs_data, team_longname)

## get list of players in the team
players = fd.get_players(picks)

# get heroes played per player
heroes_played = fd.get_heroesplayed_players(match_data, team_longname)

## caculate wr per hero per player
heroes_played_wr, heroes_played_played = fd.get_heroeswr_perplayer(players, heroes_played)

print('List of heroes and WR for each player in team ', team_longname, ':\n', heroes_played_wr, '\n')

# =============================================================================
## Heroes played by map and WR

## get list of picked heroes
bans = fd.get_bans(matchs_data, team_longname)
picks = fd.get_picks(matchs_data, team_longname)

## get list of maps and results
map_list, maps = fd.get_maplist(matchs_data)
results = fd.get_results(match_data, team_longname)

## get heroes played per map
heroes_map, bans_map = fd.get_heroesplayed_maps(map_list, maps, picks, results)

## caculate wr per hero per map
heroes_map_wr, heroes_map_played, map_bans = fd.get_heroeswr_permap(heroes_map, bans_map)
print('List of heroes and WR for each map :\n', heroes_map, '\n')

# =============================================================================


# =============================================================================
# STORE DATA IN DATAFRAMES
# =============================================================================
df_player_wr = fun.dict_to_dataframe(heroes_played_wr)
df_player_played = fun.dict_to_dataframe(heroes_played_played)
df_map_wr = fun.dict_to_dataframe(heroes_map_wr)
df_map_played = fun.dict_to_dataframe(heroes_map_played)
df_wr_bymap = pd.DataFrame.from_dict(winrate_bymap, orient='index', columns=['WR'])

## Store dataframes in an excel file ##
if save_excel == 'yes':
    fun.save_to_excel(team_shortname+'_data', [df_map_wr, df_map_played, \
                    df_player_wr, df_player_played, df_wr_bymap], \
                    ['map wr', 'map played', 'player wr', 'player played', 'total map wr'])

# =============================================================================


# =============================================================================
# DISPLAY DATA
# =============================================================================
if plot_results == 'yes':
    df_map_played, df_map_wr, df_player_played, df_player_wr = fun.sort_by_most_played(df_map_played, df_map_wr, df_player_played, df_player_wr)

    plt.figure()
    plt.suptitle(team_longname+' WR by map')
    plt.bar(range(len(winrate_bymap)), list(winrate_bymap.values()), align='center')
    plt.xticks(range(len(winrate_bymap)), list(winrate_bymap.keys()), rotation=90)
    plt.show()

    plt.figure()
    plt.suptitle(team_longname+' number of times played')
    plt.bar(range(len(number_bymap)), list(number_bymap.values()), align='center')
    plt.xticks(range(len(number_bymap)), list(number_bymap.keys()), rotation=90)
    plt.show()


    fun.display_team_stats(df_player_wr, df_player_played, team_winrate, max_player=6, team_name=team_shortname)
    fun.display_map_stats(df_map_wr, df_map_played, df_wr_bymap, team_name='JTFM')
