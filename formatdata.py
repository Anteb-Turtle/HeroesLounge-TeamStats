# -*- coding: utf-8 -*-
"""
Created on Thu Aug  8 17:39:31 2019

@author: antoine.bierret
"""

def get_results(matchs_data,team_longname):
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
def get_picks(matchs_data, team_longname):
    picks=[]
    for match in matchs_data:
        if match['teams'][0] == team_longname :
            picks=picks+match['picks_team_1']
        elif match['teams'][1] == team_longname :
            picks=picks+match['picks_team_2']
    return picks

def get_players(picks):
    players=[]
    for rd in picks:
        play=list(rd.keys())
        players=players+play
    
    players=list(set(players))   
    return players

def get_heroesplayed_players(matchs_data, team_longname):
    picks=get_picks(matchs_data, team_longname)
    players=get_players(picks)
    results=get_results(matchs_data, team_longname)
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

def get_bans(matchs_data,team_longname):
    bans=[]
    for match in matchs_data:
        if match['teams'][0] == team_longname :
            bans=bans+match['bans_team_1']
        elif match['teams'][1] == team_longname :
            bans=bans+match['bans_team_2']
    return bans

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