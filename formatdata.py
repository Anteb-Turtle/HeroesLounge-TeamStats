# -*- coding: utf-8 -*-
"""
Functions used to format and extract data from the matchs_data dictionnary
"""

def get_results(matchs_data, team_longname):
    """Returns a list containing a one for each win and a zero for each loss
    """
    results = []
    for match in matchs_data:
        results = results+[1 if m == team_longname else 0 for m in match['winners']]
    return results

def get_global_winrate(matchs_data, team_longname):
    """Computes the total winrate in %
    """
    results = get_results(matchs_data, team_longname)
    team_winrate = sum(results)/len(results)*100
    return team_winrate

def get_maplist(matchs_data):
    """Returns the lists of every map played, in order, and the list of unique map played
    Each map is identified by a string giving the map nameS
    List of unique map played: corresponds to the maps encontered at least once by the team
    """
    map_list = []
    for match in matchs_data:
        map_list = map_list+match['maps']
    map_uni = list(set(map_list))
    return map_list, map_uni

def get_map_winrate(map_list, map_uni, results):
    """ Computes the inrate of the team over each map
    Returns 3 dictionnaries with unique map names as keys.
    map_wr stores the winrate for each map
    map_w stores the number of wins for each map
    map_p stores the number of times each map was played
    """
    map_w = [0]*len(map_uni)
    map_p = [0]*len(map_uni)
    for i in range(0, len(map_uni)):
        map_p[i] = sum([1 for mapp in map_list if mapp == map_uni[i]])
        map_w[i] = sum([1 for j in range(0, len(map_list)) if ((map_list[j] == map_uni[i]) and (results[j] == 1))])

    map_wr = [map_w[i]/map_p[i]*100 for i in range(0, len(map_uni))]
    return map_wr, map_w, map_p

def get_picks(matchs_data, team_longname):
    """Returns the lists of every hero played, in order
    """
    picks = []
    for match in matchs_data:
        if match['teams'][0] == team_longname:
            picks = picks+match['picks_team_1']
        elif match['teams'][1] == team_longname:
            picks = picks+match['picks_team_2']
    return picks

def get_bans(matchs_data, team_longname):
    """Returns the lists of every hero banned, in order
    """
    bans = []
    for match in matchs_data:
        if match['teams'][0] == team_longname:
            bans = bans+match['bans_team_1']
        elif match['teams'][1] == team_longname:
            bans = bans+match['bans_team_2']
    return bans

def get_players(picks):
    """Return the list of players in the team
    """
    players = []
    for rd in picks:
        play = list(rd.keys())
        players = players+play

    players = list(set(players))
    return players

def get_heroesplayed_players(matchs_data, team_longname):
    """Returns a dict linking each player to
    - the heroes he/she played
    - if it was a win (1) or a loss (0)
    """
    picks = get_picks(matchs_data, team_longname)
    players = get_players(picks)
    results = get_results(matchs_data, team_longname)
    heroes_played = {item: [[], []] for item in players}
    for pl in players:
        i = 0
        for rd in picks:
            if pl in rd.keys():
                heroes_played[pl][0].append(rd[pl])
                if results[i] == 1:
                    heroes_played[pl][1].append(1)
                else:
                    heroes_played[pl][1].append(0)
            i += 1
    return heroes_played

def get_heroeswr_perplayer(players, heroes_played):
    """ Calculates the winrate from the heroes_played dict
    Returns 2 dicts of dicts:
        - for each player the list of heroes played and their respective winrate
        - for each player the list of heroes played and the number of rounds played
    """
    heroes_played_wr = {}
    heroes_played_played = {}
    for pl in players:
        uni = list(set(heroes_played[pl][0]))
        w = [0]*len(uni)
        p = [0]*len(uni)
        for i in range(0, len(uni)):
            p[i] = sum([1 for h in heroes_played[pl][0] if h == uni[i]])
            w[i] = sum([1 for j in range(0, len(heroes_played[pl][0])) if ((heroes_played[pl][0][j] == uni[i]) and (heroes_played[pl][1][j] == 1))])

        heroes_played_wr[pl] = {uni[key]:[w[i]/p[i]*100 for i in range(0, len(uni))][key] for key in range(0, len(uni))}
        heroes_played_played[pl] = {uni[key]:p[key] for key in range(0, len(uni))}
    return heroes_played_wr, heroes_played_played



def get_heroesplayed_maps(map_list, maps, picks, results, bans={}):
    """Returns a dict linking each map to
    - the heroes played on this map
    - if it was a win (1) or a loss (0)
    Optional: returns dict of the team's bans for each map
    """
    heroes_map = {item: [[], []] for item in maps}
    bans_map = {item: [] for item in maps}
    for mp in maps:
        i = 0
        for rd in range(0, len(map_list)):
            if mp in map_list[rd]:
                heroes_map[mp][0] += list(picks[rd].values())
                if results[i] == 1:
                    heroes_map[mp][1] += [1, 1, 1, 1, 1]
                else:
                    heroes_map[mp][1] += [0, 0, 0, 0, 0]
                if bans:
                    bans_map[mp] += list(bans[rd])
            i += 1
    return heroes_map, bans_map

def get_heroeswr_permap(maps, heroes_map, bans_map={}):
    """ Calculates the winrate from the heroes_map dict
    Returns 2 dicts of dicts:
        - for each map the list of heroes played and their respective winrate
        - for each map the list of heroes played and the number of rounds played
    Optional: dict linking map to name and number of times a hero was banned on this map
    """
    heroes_map_wr = {}
    heroes_map_played = {}
    map_bans = {}
    for mp in maps:
        uni = list(set(heroes_map[mp][0]))
        if bans_map:
            uni_ban = list(set(bans_map[mp]))
        else:
            uni_ban = {}
        w = [0]*len(uni)
        p = [0]*len(uni)
        b = [0]*len(uni_ban)
        for i in range(0, len(uni)):
            p[i] = sum([1 for h in heroes_map[mp][0] if h == uni[i]])
            w[i] = sum([1 for j in range(0, len(heroes_map[mp][0])) if ((heroes_map[mp][0][j] == uni[i]) and (heroes_map[mp][1][j] == 1))])
        for i in range(0, len(uni_ban)):
            b[i] = sum([1 for h in bans_map[mp] if h == uni_ban[i]])

        heroes_map_wr[mp] = {uni[key]:[w[i]/p[i]*100 for i in range(0, len(uni))][key] for key in range(0, len(uni))}
        heroes_map_played[mp] = {uni[key]:p[key] for key in range(0, len(uni))}
        map_bans[mp] = {uni_ban[key]:b[key] for key in range(0, len(uni_ban))}
        
    return heroes_map_wr, heroes_map_played, map_bans
