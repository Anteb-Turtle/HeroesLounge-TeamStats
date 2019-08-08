# -*- coding: utf-8 -*-
"""
Created on Thu Aug  1 16:50:34 2019

@author: antoine.bierret
"""
    
# =============================================================================
# DOC
# =============================================================================




import pandas as pd
import requests
import json
from bs4 import BeautifulSoup as soup
from matplotlib import pyplot as plt
import supportfunctions as fun
import formatdata as fd


# =============================================================================
# INPUTS
# =============================================================================
team_shortname='JTFM'
team_longname='Jaina The Frost Mage'
list_of_last_seasons=[1,2,3] # list of integers: 0 is current season, 1 is past season, ...
plot_results='yes' # 'yes' to show bar plots of statistics
#==============================================================================


# =============================================================================
# RETREIVE DATA FROM HEROESLOUNGE.GG
# =============================================================================
print('Requesting team html')
url="https://heroeslounge.gg/team/view/"+team_shortname
r = requests.get(url)
result = requests.get(url)
page = result.text
doc = soup(page,"html5")
print('Request completed')
print('\n')

# =============================================================================
## Retreive seasons list
id_list = [element.get('id') for element in doc.find_all('div')]
ids=[ i for i in id_list if ('roundmatches' in str(i))]
## Filter by season
ids=ids[1:]
ids=[ ids[i] for i in list_of_last_seasons]

# =============================================================================
## Find all matches links in filtered seasons
matches_links=[]
for id1 in ids:
    for div in doc.find_all('div', {'id': id1}):
        matches_list = div.find_all('a')
    matches_list=matches_list[1::3]
    
    matches_links=matches_links+[str(i.get('href')) for i in matches_list]
        
print(matches_links)
print('\n')

# =============================================================================
## Retreive data from each match
matchs_data=[]
match_picks=[]
for link in matches_links:
    print('Requesting link:', link)
    result1 = requests.get(link)
    print('Request completed')
    page1 = result1.text
    doc1 = soup(page1,"html5")
    games=doc1.find_all('div', {'class': 'tab-pane'})
    games_id=[i.get('id') for i in games]
    
    ## If there is a forfeit ##
    if (True in [ True for g in games if ('No Replay File found!' in g.text)]):
        print(games_id, ' no replay files found')
        continue
    ## ##
   
    ## Extract data from each game/round of the match 
    round_data=[]
    round_picks_team1=[]
    round_picks_team2=[]
    round_bans_team1=[]
    round_bans_team2=[]
    for game in games:
        heroes=[element.get('alt') for element in game.find_all('img')]
        team1=heroes[0]
        team2=heroes[1]
        teams=[team1,team2]
        heroes=heroes[2:19]
        picks=heroes[0:10]
        bans_team1=heroes[10:13]
        bans_team2=heroes[14:17]
        players=[element.text for element in game.find_all('a')]
        players=players[2:12]
        players=[' '.join(p.split()) for p in players]
        
        picks_team1=dict(zip(players[0:5],picks[0:5]))
        picks_team2=dict(zip(players[5:10],picks[5:10]))
        round_picks_team1.append(picks_team1)
        round_picks_team2.append(picks_team2)
        
        round_bans_team1.append(bans_team1)
        round_bans_team2.append(bans_team2)
        
    
    print('Match data gathered')   
            
    duration=doc1.find_all('div',{'class':"col-12 col-md-2"})
    duration=[d.text.split()[1] for d in duration]
    
    maps=doc1.find_all('span',{'class':"badge badge-info"})
    maps_played=[m.text for m in maps]
        
    winner=doc1.findAll('span', {'class':["badge badge-success float-left", "badge badge-success float-right"]})
    winner=[team1 if w.get('class')[2] =="float-right" else team2 for w in winner]
    
    ## Store all data in a dictionnary
    match_data={'match': link.split('/')[-1], 'games_id': games_id, 'teams': teams,'picks_team_1': round_picks_team1,'picks_team_2': round_picks_team2,'bans_team_1': round_bans_team1,'bans_team_2': round_bans_team2,'durations': duration,'maps': maps_played,'winners': winner}
    matchs_data.append(match_data)
    
print('---- All data gathered ----')    


## Save to JSON
with open(team_shortname+'_data.json', 'w') as file:
    json.dump(match_data, file)


# =============================================================================
    
    


# =============================================================================
# FORMAT DATA
# =============================================================================    
    
# =============================================================================
def get_results(match_data):
    results=[]
    for match in matchs_data:
        results=results+[ 1 if m == team_longname else 0 for m in match['winners']]
    return results
    
def get_global_winrate(matchs_data):
    results=get_results(matchs_data)
    team_winrate=sum(results)/len(results)*100
    return team_winrate

def get_maplist(matchs_data):
    map_list=[]
    for match in matchs_data:
        map_list=map_list+match['maps']
    map_uni=list(set(map_list))  
    return map_list, map_uni

def get_map_winrate(map_list,map_uni,results): 
    map_w=[0]*len(map_uni)
    map_p=[0]*len(map_uni)
    for i in range(0,len(map_uni)):
        map_p[i]=sum([1 for mapp in map_list if mapp == map_uni[i]])
        map_w[i]=sum([1 for j in range(0,len(map_list)) if ((map_list[j] == map_uni[i]) and (results[j]==1))])
    
    map_wr=[map_w[i]/map_p[i]*100 for i in range(0,len(map_uni))]
    return map_wr, map_w, map_p

## Total WR
    
## Total and Map winrate
map_list, map_uni = fd.get_maplist(matchs_data)
results = fd.get_results(match_data)
team_winrate = fd.get_global_winrate(matchs_data)
print(team_longname, ' total winrate over chosen seasons: \n', team_winrate, '%\n')    

## Map WR
map_wr, map_w, map_p = fd.get_map_winrate(map_list,map_uni,results)

winrate_bymap=dict(zip(map_uni,map_wr))
print('Winrate by map :\n',winrate_bymap,'\n')
number_bymap=dict(zip(map_uni,map_p))
print('Number of times map played :\n',number_bymap,'\n')

# =============================================================================
## Heroes played by player and WR

## get list of picked heroes
def get_picks(matchs_data, team_longname):
    picks=[]
    for match in matchs_data:
        if match['teams'][0] == team_longname :
            picks=picks+match['picks_team_1']
        elif match['teams'][1] == team_longname :
            picks=picks+match['picks_team_2']
    return picks

picks = fd.get_picks(matchs_data, team_longname)

## get list of players in the team
def get_players(picks):
    players=[]
    for rd in picks:
        play=list(rd.keys())
        players=players+play
    
    players=list(set(players))   
    return players

players = fd.get_players(picks)

# get heroes played per player
def get_heroesplayed_players(match_data, team_longname):
    picks=get_picks(matchs_data, team_longname)
    players=get_players(picks)
    heroes_played={item: [[],[]] for item in players}
    for pl in players:
        i=0
        for rd in picks:
            if pl in rd.keys():
                heroes_played[pl][0].append(rd[pl])
                if results[i] == 1:
                    heroes_played[pl][1].append(1)
                else:
                    heroes_played[pl][1].append(0)
            i+=1
    return heroes_played

heroes_played = fd.get_heroesplayed_players(match_data, team_longname)

# caculate wr per hero per player
def get_heroeswr_perplayer(players,heroes_played):
    heroes_played_wr={}
    heroes_played_played={}
    for pl in players:
        uni=list(set(heroes_played[pl][0]))   
        w=[0]*len(uni)
        p=[0]*len(uni)
        for i in range(0,len(uni)):
            p[i]=sum([1 for h in heroes_played[pl][0] if h == uni[i]])
            w[i]=sum([1 for j in range(0,len(heroes_played[pl][0])) if ((heroes_played[pl][0][j] == uni[i]) and (heroes_played[pl][1][j]==1))])
        
        heroes_played_wr[pl]={uni[key]:[w[i]/p[i]*100 for i in range(0,len(uni))][key] for key in range(0,len(uni))}  
        heroes_played_played[pl]={uni[key]:p[key] for key in range(0,len(uni))}  
    return heroes_played_wr,heroes_played_played

heroes_played_wr, heroes_played_played = fd.get_heroeswr_perplayer(heroes_played)

print('List of heroes and WR for each player in team ', team_longname, ':\n',heroes_played_wr,'\n')    
    
# =============================================================================
## Heroes played by map and WR
    
## get list of picked heroes
def get_bans(matchs_data,team_longname):
    bans=[]
    for match in matchs_data:
        if match['teams'][0] == team_longname :
            bans=bans+match['bans_team_1']
        elif match['teams'][1] == team_longname :
            bans=bans+match['bans_team_2']
    return bans

bans=fd.get_bans(matchs_data,team_longname)
picks=fd.get_picks(matchs_data,team_longname)

## get list of maps and results
map_list, maps = fd.get_maplist(matchs_data)
results = fd.get_results(match_data)

## get heroes played per map
def get_heroesplayed_maps(map_list,maps,picks,results,bans={}):
    heroes_map={item: [[],[]] for item in maps}
    bans_map={item: [] for item in maps}
    for mp in maps:
        i=0
        for rd in range(0,len(map_list)):
            if mp in map_list[rd]:
                heroes_map[mp][0]+=list(picks[rd].values())
                if results[i] == 1:
                    heroes_map[mp][1]+=[1,1,1,1,1]
                else:
                    heroes_map[mp][1]+=[0,0,0,0,0]
                if len(bans) > 0 :
                    bans_map[mp]+=list(bans[rd])
            i+=1
    return heroes_map, bans_map

heroes_map, bans_map = fd.get_heroesplayed_maps(map_list, maps,picks,results)

## caculate wr per hero per map
def get_heroeswr_permap(maps,heroes_map,bans_map={}):
    heroes_map_wr={}
    heroes_map_played={}
    map_bans={}
    for mp in maps:
        uni=list(set(heroes_map[mp][0]))
        if len(bans_map) > 0 :
            uni_ban=list(set(bans_map[mp]))  
        else :
            uni_ban={}
        w=[0]*len(uni)
        p=[0]*len(uni)
        b=[0]*len(uni)
        for i in range(0,len(uni)):
            p[i]=sum([1 for h in heroes_map[mp][0] if h == uni[i]])
            w[i]=sum([1 for j in range(0,len(heroes_map[mp][0])) if ((heroes_map[mp][0][j] == uni[i]) and (heroes_map[mp][1][j]==1))])
        for i in range(0,len(uni_ban)):  
            b[i]=sum([1 for h in bans_map[mp] if h == uni_ban[i]])
            
        heroes_map_wr[mp]={uni[key]:[w[i]/p[i]*100 for i in range(0,len(uni))][key] for key in range(0,len(uni))}
        heroes_map_played[mp]={uni[key]:p[key] for key in range(0,len(uni))} 
        map_bans={uni_ban[key]:b[key] for key in range(0,len(uni_ban))} 
    return heroes_map_wr,heroes_map_played,map_bans

heroes_map_wr,heroes_map_played,map_bans = fd.get_heroeswr_permap(heroes_map,bans_map)
print('List of heroes and WR for each map :\n',heroes_map,'\n')    

# =============================================================================


# =============================================================================
# STORE DATA IN DATAFRAMES
# =============================================================================
df_player_wr=fun.dict_to_dataframe(heroes_played_wr)
df_player_played=fun.dict_to_dataframe(heroes_played_played)
df_map_wr=fun.dict_to_dataframe(heroes_map_wr)
df_map_played=fun.dict_to_dataframe(heroes_map_played)
df_wr_bymap=pd.DataFrame.from_dict(winrate_bymap,orient='index',columns=['WR'])

## Store dataframes in an excel file ##
fun.save_to_excel(team_shortname+'_data',[df_map_wr,df_map_played,df_player_wr,df_player_played,df_wr_bymap],['map wr','map played','player wr','player played','total map wr'])    

# =============================================================================


# =============================================================================
# DISPLAY DATA    
# =============================================================================
if plot_results == 'yes':
    df_map_played,df_map_wr,df_player_played,df_player_wr=fun.sort_by_most_played(df_map_played,df_map_wr,df_player_played,df_player_wr)
    
    plt.figure()
    plt.suptitle(team_longname+' WR by map')
    plt.bar(range(len(winrate_bymap)), list(winrate_bymap.values()), align='center')
    plt.xticks(range(len(winrate_bymap)), list(winrate_bymap.keys()),rotation=90)
    plt.show()  
    
    plt.figure()
    plt.suptitle(team_longname+' number of times played')
    plt.bar(range(len(number_bymap)), list(number_bymap.values()), align='center')
    plt.xticks(range(len(number_bymap)), list(number_bymap.keys()),rotation=90)
    plt.show()  
    
    
    fun.display_team_stats(df_player_wr, df_player_played,team_winrate,max_player=6,team_name=team_shortname)
    fun.display_map_stats(df_map_wr, df_map_played,df_wr_bymap,team_name='JTFM')

    
    
    
    
    
    
    