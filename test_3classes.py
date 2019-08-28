# -*- coding: utf-8 -*-
""" Classes defninitions
"""

import json
import pandas as pd
import requests
from bs4 import BeautifulSoup as soup
from matplotlib import pyplot as plt
import supportfunctions as fun
import formatdata as fd
import datetime as dt

class Team():
    """ This class is just a common init method for the others classes
    """
    def __init__(self, shortname, longname, list_of_last_seasons=[]):
        self.matchs_list = []
        self.team_shortname = shortname
        self.team_longname = longname
        self.seasons = list_of_last_seasons

class TeamRawData(Team):
    """Load and save raw data from heroeslounge.gg
    Use either gather_online_data() or load_from_json() to create
    a list of dict containing all data from the selected seasons for the team
    """
    def __init__(self, shortname, longname, list_of_last_seasons=[], **kwargs):
        super().__init__(shortname, longname, list_of_last_seasons)
        
        if 'filename' in kwargs:
            filename = kwargs.get('filename')
            self.load_from_json(filename)
        elif 'gather_online' in kwargs:
            gather = kwargs.get('gather_online')
            if gather == True:
                self.gather_online_data()

    def set_seasons(self, seasons_list):
        """ Set the seasons to be searched on heroeslounge.gg
        season_list can be a list of integers or a list of strings
        list of integers:
            0 is current season
            1 is last season
            2 is the season before last season ...
        list of strings: enter the complete name of each season
        Warning: playoffs and aram cups count as seasons
        """
        self.seasons = seasons_list

    def add_season(self, seasons_list):
        """ Append a list of seasons to the current one
        """
        self.seasons.append(seasons_list)

    def set_names(self, shortname, longname):
        """ Set team tag and team name
        """
        self.team_shortname = shortname
        self.team_longname = longname

    def gather_online_data(self, opt_seasons=[]):
        """ Reteives inforamtion from Heroeslounge.gg
        Computes the matchs_list dict containing all raw datas from the team
        """
        if not (self.seasons and opt_seasons):
            print('Please specify the seasons your are interested in')
            print('Trying with current season')
            list_of_last_seasons = [0]
        if not opt_seasons:
            list_of_last_seasons = self.seasons
        else:
            list_of_last_seasons = opt_seasons

        print('Requesting team html')
        url = "https://heroeslounge.gg/team/view/" + self.team_shortname
        result = requests.get(url)
        page = result.text
        doc = soup(page, features="html5lib")
        print('Request completed')
        print('\n')

        # =============================================================================
        ## Retreive seasons list
        id_list = [element.get('id') for element in doc.find_all('div')]
        ids = [i for i in id_list if 'roundmatches' in str(i)]
        ## Filter by season
        ids = ids[1:]

        test=doc.find('div',{'id':'roundmatches_groups'})
        ids = [a.get('href')[1:] for a in test.find_all('a')]
        if all(isinstance(season,int) for season in list_of_last_seasons): # filter using list of strings
             ids = [ids[i] for i in list_of_last_seasons]
        elif all(isinstance(season,str) for season in list_of_last_seasons): # filter using the names of the seasons
             names = [li.text.rstrip().lstrip() for li in test.find_all('li')]
             names = [names.index(name) for name in names if name in list_of_last_seasons]
             ids = [ids[i] for i in names]
        else:
             raise AttributeError('list_of_last_seasons wrong type')

        
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
        for link in matches_links:
            print('Requesting link:', link)
            result1 = requests.get(link)
            print('Request completed')
            page1 = result1.text
            doc1 = soup(page1, features="html5lib")
            games = doc1.find_all('div', {'class': 'tab-pane'})
            games_id = [i.get('id') for i in games]

            ## In case the match has not been scheduled ##
            if "The match has not been scheduled yet!" in doc1.text:
                print('The match has not been scheduled yet')
                continue
            ## ##
            ## In case the match is scheduled in the future##
            time = doc1.find('div', {'id': 'matchtime'})
            time = time.find('h3').text
            time = '-'.join(str(time).split()[2:])
            time = dt.datetime.strptime(time,"%d-%b-%Y-%H:%M")
            if time > dt.datetime.now() :
                print('The match has not been played yet')
                continue
            ## ##
            ## In case there is a forfeit ##
            if (True in [True for g in games if 'No Replay File found!' in g.text]):
                print(games_id, ' no replay files found')
                continue
            ## ##

            ## Extract data from each game/round of the match
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

        self.matchs_list = matchs_data
        return self


    def save_to_json(self, opt_filename=None):
        """Save raw data to a json file
        Filename is opt_filename if used, else defaults to team_shortname
        """
        if not opt_filename:
            name = self.team_shortname+'_data.json'
        else:
            name = opt_filename

        if self.matchs_list:
            with open(name, 'w') as file:
                json.dump(self.matchs_list, file)
            print('Data saved to: '+name)
        else:
            print('No data found in matchs_list')

    def load_from_json(self, filename):
        """ Load matchs_list dict containing all raw data from the team
        """
        with open(filename, 'r') as file:
            self.matchs_list = json.load(file)


class TeamProcessedData(Team):
    """ Extracts useful data from a TeamRawData object
    Processed data data is stored in a number of dictionnaries
    """
    def __init__(self, raw_data):
        super().__init__(raw_data.team_shortname, raw_data.team_longname, raw_data.seasons)
        self.get_formatted_data(raw_data)

    def get_formatted_data(self, raw_data):
        """ Computes dicts with all stats from the matchs_list dict
        """
        self.map_list, self.map_uni = fd.get_maplist(raw_data.matchs_list)
        self.results = fd.get_results(raw_data.matchs_list, self.team_longname)
        self.team_winrate = fd.get_global_winrate(raw_data.matchs_list, self.team_longname)
#        print(team_longname, ' total winrate over chosen seasons: \n', team_winrate, '%\n')

        ## Map WR
        self.map_wr, self.map_w, self.map_p = fd.get_map_winrate(self.map_list, self.map_uni, self.results)
        self.winrate_bymap = dict(zip(self.map_uni, self.map_wr))
#        print('Winrate by map :\n', self.winrate_bymap, '\n')
        self.number_bymap = dict(zip(self.map_uni, self.map_p))
#        print('Number of times map played :\n', number_bymap, '\n')

        # =============================================================================
        ## Heroes played by player and WR
        ## get list of picked heroes
        self.picks = fd.get_picks(raw_data.matchs_list, self.team_longname)
        self.bans = fd.get_bans(raw_data.matchs_list, self.team_longname)
        ## get list of players in the team
        self.players = fd.get_players(self.picks)
        # get heroes played per player
        self.heroes_played = fd.get_heroesplayed_players(raw_data.matchs_list, self.team_longname)
        ## caculate wr per hero per player
        self.heroes_played_wr, self.heroes_played_played = fd.get_heroeswr_perplayer(self.players, self.heroes_played)
#        print('List of heroes and WR for each player in team ', team_longname, ':\n', heroes_played_wr, '\n')

        # =============================================================================
        ## Heroes played by map and WR
        ## get heroes played per map
        self.heroes_map, self.bans_map = fd.get_heroesplayed_maps(self.map_list, self.map_uni, self.picks, self.results, self.bans)
        ## caculate wr per hero per map
        self.heroes_map_wr, self.heroes_map_played, self.map_bans = fd.get_heroeswr_permap(self.map_uni, self.heroes_map, self.bans_map)
#        print('List of heroes and WR for each map :\n', heroes_map_wr, '\n')

#        list_of_dicts = [self.heroes_played_wr, self.heroes_played_played, self.heroes_map_wr, self.heroes_map_played, self.winrate_bymap, self.map_bans]
        return self

class TeamDisplayData(Team):
    """ Convert dictionaries from a TeamProcessedData object to dataframes and
    plots them. Displays the differents stats for players/maps.
    Dataframes can be loaded from:
        - raw data from TeamRawData object
        - Processed data from TeamProcessedData objetc
        - loaded from excel file
    """
    def __init__(self, **kwargs):
        #processed_data
        #raw_data
        #filename + team_winrate
        if 'processed_data' in kwargs:
            processed_data = kwargs.get('processed_data')
            super().__init__(processed_data.team_shortname, processed_data.team_longname, processed_data.seasons)
            self.team_winrate = processed_data.team_winrate
            self.get_dataframes(processed_data)
        elif 'raw_data' in kwargs:
            raw_data = kwargs.get('raw_data')
            super().__init__(raw_data.team_shortname, raw_data.team_longname, raw_data.seasons)
            if not raw_data.matchs_list:
                print('Raw data is empty. Trying to retreive online data.')
                raw_data.gather_online_data()
            processed = TeamProcessedData(raw_data)
            self.team_winrate = processed.team_winrate
            self.get_dataframes(processed)
        elif 'filename' in kwargs:
            filename = kwargs.get('filename')
            winrate = kwargs.get('winrate')
            shortname = kwargs.get('shortname')
            longname = kwargs.get('longname')
            seasons = kwargs.get('seasons')
            super().__init__(shortname, longname, seasons)
            self.team_winrate = winrate
            self.load_from_excel(filename)
        else:
            print('Empty TeamDisplayData')
            super().__init__('', '')
            self.winrate = None

    def get_dataframes(self, processed_data):
        """Converts dicts to dataframes
        """
        self.df_player_wr = fun.dict_to_dataframe(processed_data.heroes_played_wr)
        self.df_player_played = fun.dict_to_dataframe(processed_data.heroes_played_played)
        self.df_map_wr = fun.dict_to_dataframe(processed_data.heroes_map_wr)
        self.df_map_played = fun.dict_to_dataframe(processed_data.heroes_map_played)
        self.df_wr_bymap = pd.DataFrame.from_dict(processed_data.winrate_bymap, orient='index', columns=['WR'])
        self.df_bans_map = fun.dict_to_dataframe(processed_data.map_bans)

        return self

    def save_to_excel(self, opt_filename=None):
        """Save all dataframes to an excel file
        Filename is opt_filename if used, else defaults to team_shortname
        """
        if not opt_filename:
            name = self.team_shortname+'.xlsx'
        else:
            name = opt_filename

        try:
            df_list = [self.df_player_wr, self.df_player_played, self.df_map_wr, self.df_map_played, self.df_wr_bymap, self.df_bans_map]
            list_of_datatypes = ['map wr', 'map played', 'player wr', 'player played', 'map bans', 'total map wr']
        except AttributeError:
            print('No dataframes found.\n Method get_dataframes should be used before calling save_to_excel')
            return
        # Create a Pandas Excel writer using XlsxWriter
        writer = pd.ExcelWriter(name, engine='xlsxwriter')
        i = 0
        for df in df_list:
            # Convert the dataframe to an XlsxWriter Excel object
            df.to_excel(writer, sheet_name=list_of_datatypes[i])
            i += 1

        writer.save()
        print('Data saved to: '+name)

    def load_from_excel(self, filename):
        """ Load the dataframes used for statistics visualization
        """
        df_list = []
        for sheet in ['map wr', 'map played', 'player wr', 'player played', 'map bans', 'total map wr']:
            df_list.append(pd.read_excel(filename, sheet_name=sheet).set_index('Unnamed: 0'))

        self.df_player_wr = df_list[0]
        self.df_player_played = df_list[1]
        self.df_map_wr = df_list[2]
        self.df_map_played = df_list[3]
        self.df_wr_bymap = df_list[4]
        self.df_bans_map = df_list[5]

        return self

    def display_player_stats(self, players):
        """ Plots the winrate for a number of players from the team
        - if player is an integer: displays the stats for the first "players" players in the team
        (sorted by number of matches played)
        - if player is a list of strings: displays the stats for each player in the list
        """
        plt.rc('font',size=8)
        if isinstance(players, int): # displays the stats for the first players
            n_lines = (players-1)//3+1
            fig, ax = plt.subplots(n_lines, 3)
            i = 0
            for player in list(self.df_player_wr.iloc[0:players, :].index):
                if n_lines > 1:
                    fun.team_stats_subplot(self.df_player_wr, self.df_player_played, self.team_winrate, ax[i//3, i%3], name=player, team_name=self.team_shortname)
                else:
                    fun.team_stats_subplot(self.df_player_wr, self.df_player_played, self.team_winrate, ax[i], name=player, team_name=self.team_shortname)
                i += 1

        elif isinstance(players, list): # displays the stats for the given list of players
            n_lines = (len(players)-1)//3+1
            fig, ax = plt.subplots(n_lines, 3)
            i = 0
            for player in players:
                if n_lines > 1:
                    fun.team_stats_subplot(self.df_player_wr, self.df_player_played, self.team_winrate, ax[i//3, i%3], name=player, team_name=self.team_shortname)
                else:
                    fun.team_stats_subplot(self.df_player_wr, self.df_player_played, self.team_winrate, ax[i], name=player, team_name=self.team_shortname)
                i += 1

        else:
            print('Variable players: wrong type')
            return

        plt.tight_layout()
        plt.show()

    def display_map_bans(self, bans=None):
        """ Displays a bar plot of banned heroes for each map
        """
        if bans is None:
            N = len(self.df_bans_map.index)
            n_lines = N//3+1
            fig, ax = plt.subplots(n_lines, 3)

            i = 0
            for maps in list(self.df_bans_map.iloc[0:N, :].index):
                fun.team_stats_subplot(self.df_bans_map, self.df_bans_map, 0, ax[i//3, i%3], name=maps, team_name=self.team_shortname, bans=True)
                i += 1
        elif isinstance(bans, int):
            n_lines = (bans-1)//3+1
            fig, ax = plt.subplots(n_lines, 3)
            i = 0
            for mapp in list(self.df_bans_map.iloc[0:bans, :].index):
                if n_lines > 1:
                    fun.team_stats_subplot(self.df_bans_map, self.df_bans_map, 0, ax[i//3, i%3], name=mapp, team_name=self.team_shortname, bans=True)
                else:
                    fun.team_stats_subplot(self.df_bans_map, self.df_bans_map, 0, ax[i], name=mapp, team_name=self.team_shortname, bans=True)
                i += 1
        elif isinstance(bans, list):
            n_lines = (len(bans)-1)//3+1
            fig, ax = plt.subplots(n_lines, 3)
            i = 0
            for mapp in bans:
                if n_lines > 1:
                    fun.team_stats_subplot(self.df_bans_map, self.df_bans_map, 0, ax[i//3, i%3], name=mapp, team_name=self.team_shortname, bans=True)
                else:
                    fun.team_stats_subplot(self.df_bans_map, self.df_bans_map, 0, ax[i], name=mapp, team_name=self.team_shortname, bans=True)
                i += 1
        else:
            print('Variable bans: wrong type')
        plt.tight_layout()
        plt.show()

    def display_map_stats(self, maps=None):
        """ Displays a bar plot of heroes WR and number played for a player or a map
        """
        if maps is None:
            N = len(self.df_map_wr.index)
            ax = [None]*9
            fig, ((ax[0], ax[1], ax[2]), (ax[3], ax[4], ax[5]), (ax[6], ax[7], ax[8])) = plt.subplots(3, 3)
            i = 0
            for mapp in list(self.df_map_wr.iloc[0:N, :].index):
                fun.team_stats_subplot(self.df_map_wr, self.df_map_played, self.df_wr_bymap.loc[mapp, :], ax[i], name=mapp, team_name=self.team_shortname)
                i += 1
        elif isinstance(maps, int):
            n_lines = (maps-1)//3+1
            fig, ax = plt.subplots(n_lines, 3)
            i = 0
            for mapp in list(self.df_map_wr.iloc[0:maps, :].index):
                if n_lines > 1:
                    fun.team_stats_subplot(self.df_map_wr, self.df_map_played, self.df_wr_bymap.loc[mapp, :], ax[i//3, i%3], name=mapp, team_name=self.team_shortname)
                else:
                    fun.team_stats_subplot(self.df_map_wr, self.df_map_played, self.df_wr_bymap.loc[mapp, :], ax[i], name=mapp, team_name=self.team_shortname)
                i += 1
        elif isinstance(maps, list):
            n_lines = (len(maps)-1)//3+1
            fig, ax = plt.subplots(n_lines, 3)
            i = 0
            for mapp in maps:
                if n_lines > 1:
                    fun.team_stats_subplot(self.df_map_wr, self.df_map_played, self.df_wr_bymap.loc[mapp, :], ax[i//3, i%3], name=mapp, team_name=self.team_shortname)
                else:
                    fun.team_stats_subplot(self.df_map_wr, self.df_map_played, self.df_wr_bymap.loc[mapp, :], ax[i], name=mapp, team_name=self.team_shortname)
                i += 1
        else:
            print('Variable maps: wrong type')

        plt.tight_layout()
        plt.show() 
