import teamclasses as tc
import supportfunctions as fun
import ipywidgets as widgets
from ipywidgets import interact, interact_manual, interactive
from IPython.display import display
import plotly.express as px
import pandas as pd
import numpy as np
import datetime as dt

class TeamWidget(tc.TeamRawData):
    
    def __init__(self, tag = 'Turtles', name='Turtle Team', n = [0]):
        ## Set the widgets and display them
        top_header = widgets.HTML(value='<h1 style="font-size:20px;">HeroesLounge-TeamStats Dashboard</h1>'+
                                  '<p>Enter team info and click "Check team", select seasons and click "Submit and run" button. '+
                                  'Wait for the data to be collected from heroeslounge.gg and then click "Display figures".</p>'+
                                  '<p>Source code is available at https://github.com/Anteb-Turtle/HeroesLounge-TeamStats</p>')
        tag_label = widgets.Label(value='Team tag:')
        self.team_tag = widgets.Text(tag)
        self.team_label = widgets.Label(value="Tag can be found in the team's URL on heroeslounge.gg")
        self.w_seasons = widgets.SelectMultiple(options=[0,1,2,3,4,5,6,7,8,9],
                                        value= n,
                                        description='seasons',
                                        disabled=True)
        button0 = widgets.Button(description="Check team")
        self.button1 = widgets.Button(description="Submit and run", disabled=True)
        self.button2 = widgets.Button(description="Display figures", disabled=True)
        self.label0 = widgets.Label(value='')
        self.label1 = widgets.Label(value='')
        self.label2 = widgets.Label(value='')
        self.label_error = widgets.Label(value='')
        self.progress = widgets.IntProgress(value=0, min=0, max=10,bar_style='')
        
        self.out1, self.out2, self.out3, self.out4 = widgets.Output(), widgets.Output(), widgets.Output(), widgets.Output()
        
        buttonlabel0 = widgets.HBox([button0, self.label0])
        buttonlabel1 = widgets.HBox([self.button1, self.label1])
        buttonlabel2 = widgets.HBox([self.button2, self.label2])
        left_side = widgets.VBox([tag_label, self.team_tag, 
                                  self.team_label, buttonlabel0,
                                  self.w_seasons, buttonlabel1, 
                                  self.progress, buttonlabel2,
                                  self.label_error])
        right_side = widgets.Tab()
        right_side.children = [self.out1, self.out2, self.out3, self.out4]
        right_side_titles = ['All players scatter plot', 'All maps scatter plot',
                             'Individual player stats', 'Individual map stats']
        for i in range(len(right_side.children)):
            right_side.set_title(i, right_side_titles[i])
        
        box = widgets.AppLayout(header=top_header,
          left_sidebar=left_side,
          center=right_side,
          right_sidebar=None,
          footer=None)
        
        button0.on_click(self.instantiate)
        self.button1.on_click(self.submit_input)
        self.button2.on_click(self.plotter)
        
        display(box)
        
    def instantiate(self, *args): 
        ## Called only when the button0 is pressed
        self.label0.value = 'Checking...'
        super().__init__(self.team_tag.value, longname = None)
        self.label_error.value, self.progress.bar_style = fun.check_http_error(self.team_doc)
        
        if self.team_longname:
            self.team_label.value = "Team name: " + self.team_longname 
        else:
            self.team_label.value = "Error in team name"

        if hasattr(self, 'seasons_names'):
            if self.seasons_names:
                self.w_seasons.options = self.seasons_names
                self.w_seasons.disabled = False
                self.button1.disabled = False
                self.label0.value = 'Done'
            else:
                self.label_error.value = f"Cannot find played seasons for team {self.team_tag.value}"
                self.label0.value = 'Error'
        else:
            self.label0.value = 'Error'
        
    def submit_input(self, *args):
        ## Called only when the button1 is pressed
        list_seasons = [self.all_seasons[i] for i,n in enumerate(self.seasons_names) if n in self.w_seasons.value]
        self.set_seasons(list_seasons)
        ## Import data
        self.label1.value = 'Wait...'
        self.gather_online_data()
        ## Process data: convert to dataframes
        self.team_display = tc.TeamDisplayData(raw_data = self)
        self.button2.disabled = False
        self.label1.value = 'Done'
        return self.team_display
    
    def plotter(self, *args):
        ## Called only when the button2 is pressed
        if hasattr(self, 'team_display'):
            self.label2.value = 'Wait...'
            with self.out1:
                fig1 = self.players_scatter()
            with self.out2:
                fig2 = self.maps_scatter()
            with self.out3:
                fig3 = self.per_player()
            with self.out4:
                fig4 = self.per_map()
            self.label2.value = 'Done'
            return fig1, fig2, fig3, fig4
        else:
            return
    
    def players_scatter(self, *args):
        tidy_players = (self.team_display.df_player_wr * self.team_display.df_player_played).sum(axis=0)
        tidy_players = pd.concat([tidy_players, self.team_display.df_player_played.sum(axis=0)], axis=1)
        tidy_players.columns = ['WR', 'played']
        tidy_players['WR'] = tidy_players['WR'] / tidy_players['played']
        tidy_players.reset_index(inplace=True)
        
        # Shifting annotations
        shift = [(0,12), (0,-10), (30,0),(-35,0),(-40,12)]
        tidy_players = tidy_players.sort_values(by=['WR','played'])
        tidy_players['shift'] = [0]*len(tidy_players.index)
        for ind in range(1, len(tidy_players.index)):
            if np.all(np.array(tidy_players.iloc[ind,1:4]) == np.array(tidy_players.iloc[ind-1,1:4])):
                tidy_players.iloc[ind,3] += 1
            elif np.all(np.array(tidy_players.iloc[ind,1:4]) == np.array(tidy_players.iloc[ind-2,1:4])):
                tidy_players.iloc[ind,3] += 2
            elif np.all(np.array(tidy_players.iloc[ind,1:4]) == np.array(tidy_players.iloc[ind-3,1:4])):
                tidy_players.iloc[ind,3] += 3
            elif np.all(np.array(tidy_players.iloc[ind,1:4]) == np.array(tidy_players.iloc[ind-4,1:4])):
                tidy_players.iloc[ind,3] += 4
         
        fig = px.scatter(tidy_players, x='played', y='WR', color='WR', size='played')
        
        for index, row in tidy_players.iterrows():
            fig.add_annotation(dict(font=dict(size=12),
                            x=row['played'],
                            y=row['WR'],
                            showarrow=False,
                            text=row['index'],
                            xshift=shift[row['shift']][0],
                            yshift=shift[row['shift']][1],
                            xref="x",
                            yref="y"))
        fig.update_layout(shapes=[
            dict(
              type= 'line',
              line = dict(color='grey', width=1, dash='dash'),
              yref= 'y', y0= self.team_display.team_winrate, y1= self.team_display.team_winrate,
              xref= 'x', x0= 0, x1= max(tidy_players.played+1)
            )
        ])
        fig.show()
        return fig
    
    def maps_scatter(self, *args):   
        tidy_maps = self.team_display.df_wr_bymap
        tidy_maps = pd.concat([tidy_maps, self.team_display.df_map_played.sum(axis=1)/5], axis=1)
        tidy_maps.columns = ['WR', 'played']
        tidy_maps.reset_index(inplace=True)
        
        # Shifting annotations
        shift = [(0,12), (0,-10), (30,0),(-35,0),(-40,12)]
        tidy_maps = tidy_maps.sort_values(by=['WR','played'])
        tidy_maps['shift'] = [0]*len(tidy_maps.index)
        for ind in range(1, len(tidy_maps.index)):
            if np.all(np.array(tidy_maps.iloc[ind,1:4]) == np.array(tidy_maps.iloc[ind-1,1:4])):
                tidy_maps.iloc[ind,3] += 1
            elif np.all(np.array(tidy_maps.iloc[ind,1:4]) == np.array(tidy_maps.iloc[ind-2,1:4])):
                tidy_maps.iloc[ind,3] += 2
            elif np.all(np.array(tidy_maps.iloc[ind,1:4]) == np.array(tidy_maps.iloc[ind-3,1:4])):
                tidy_maps.iloc[ind,3] += 3
            elif np.all(np.array(tidy_maps.iloc[ind,1:4]) == np.array(tidy_maps.iloc[ind-4,1:4])):
                tidy_maps.iloc[ind,3] += 4
                
        fig = px.scatter(tidy_maps, x='played', y='WR', color='WR', size='played')
        
        for index, row in tidy_maps.iterrows():
            fig.add_annotation(dict(font=dict(size=12),
                            x=row['played'],
                            y=row['WR'],
                            showarrow=False,
                            text=row['index'],
                            xshift=shift[row['shift']][0],
                            yshift=shift[row['shift']][1],
                            xref="x",
                            yref="y"))
        fig.update_layout(shapes=[
            dict(
              type= 'line',
              line = dict(color='grey', width=1, dash='dash'),
              yref= 'y', y0= self.team_display.team_winrate, y1= self.team_display.team_winrate,
              xref= 'x', x0= 0, x1= max(tidy_maps.played+1)
            )
        ])
        fig.show()
        return fig
    
    def per_player(self, *args):
        disp1 = pd.melt(self.team_display.df_player_wr.reset_index(), id_vars=['index'], var_name='hero', value_name='WR')
        disp2 = pd.melt(self.team_display.df_player_played.reset_index(), id_vars=['index'], var_name='hero', value_name='played')
        disp = pd.merge(disp1,disp2, how='outer')
        disp = disp.fillna(0)
        #plotting
        fig = px.scatter(disp, x='hero', y='index', size='played', color='WR')
        fig.show()
        return fig

    def per_map(self, *args):
        disp1 = pd.melt(self.team_display.df_map_wr.reset_index(), id_vars=['index'], var_name='hero', value_name='WR')
        disp2 = pd.melt(self.team_display.df_map_played.reset_index(), id_vars=['index'], var_name='hero', value_name='played')
        disp3 = pd.melt(self.team_display.df_bans_map.reset_index(), id_vars=['index'], var_name='hero', value_name='banned')
        disp = pd.merge(pd.merge(disp1,disp2, how='outer'),disp3, how='outer')
        disp = disp.fillna(0)
        disp.groupby(by=['index','hero'], as_index=False).sum()
        disp['ocurence'] = disp['played'] + disp['banned']
        disp = disp[disp.played != 0]
        #plotting
        fig = px.scatter(disp, x='hero', y='index', size='ocurence', color='WR', text=disp['played'])
        fig.show()
        return fig
    
    def gather_online_data(self, opt_seasons=[]):
        """ Reteives inforamtion from Heroeslounge.gg
        Computes the matchs_list dict containing all raw datas from the team
        """
        if not (self.seasons or opt_seasons):
            print('Please specify the seasons your are interested in')
            print('Trying with current season')
            list_of_last_seasons = [0]
        if not opt_seasons:
            list_of_last_seasons = self.seasons
        else:
            list_of_last_seasons = opt_seasons
        
        # =============================================================================
        ## Retreive seasons list
        ids = self._filter_season_list(self.all_seasons, list_of_last_seasons)
        
        # =============================================================================
        ## Find all matches links in filtered seasons
        matches_links = self._find_links(self.team_doc, ids)
        self.progress.max = len(matches_links)
        self.progress.bar_style = ''
        self.progress.value = 0

        # =============================================================================
        ## Retreive data from each match
        matchs_data = []
        for link in matches_links:
            self.progress.bar_style = ''
            doc1, games, games_id = self._retreive_link(link)
            self.label_error.value, self.progress.bar_style = fun.check_http_error(doc1)
            
            ## In case there is a forfeit ##
            if (True in [True for g in games if 'No Replay File found!' in g.text]):
                print(games_id, ' no replay files found')
                self.progress.bar_style = 'info'
                continue
            ## In case the match has not been scheduled ##
            if "The match has not been scheduled yet!" in doc1.text:
                print('The match has not been scheduled yet')
                self.progress.bar_style = 'info'
                continue
            ## In case the match is scheduled in the future##
            time = doc1.find('div', {'id': 'matchtime'})
            time = time.find('h3').text
            time = '-'.join(str(time).split()[2:])
            try: 
                time = dt.datetime.strptime(time,"%d-%b-%Y-%H:%M")
                if dt.datetime.now() < (time + dt.timedelta(hours=1, minutes=15)):
                    print('The match has not been played yet')
                    self.progress.bar_style = 'info'
                    continue
            except ValueError:
                print(games_id, ' : Wrong date format. Match ignored')
                self.progress.bar_style = 'warning'
                continue
            ## ##
            
            ## Extract data from each game/round of the match
            round_picks_team1 = []
            round_picks_team2 = []
            round_bans_team1 = []
            round_bans_team2 = []
            durations = []
            maps_played = []
            winners = []
            i = 0
            for game in games:
                teams_, picks_team1, picks_team2, bans_team1, bans_team2, duration, map_played, winner = self._retreive_game_data(game)
                if i ==0:
                    teams = teams_
                #TODO: attribuer les picks+autres valeur à une liste en fonction de "teams"
                if teams == teams_:
                    round_picks_team1.append(picks_team1)
                    round_picks_team2.append(picks_team2)
                    round_bans_team1.append(bans_team1)
                    round_bans_team2.append(bans_team2)
                else:
                    round_picks_team2.append(picks_team1)
                    round_picks_team1.append(picks_team2)
                    round_bans_team2.append(bans_team1)
                    round_bans_team1.append(bans_team2)
                durations.append(duration)
                maps_played.append(map_played)
                winners.append(winner)
                i += 1

            print('Match data gathered')
            self.progress.value += 1

            ## Store all data in a dictionnary
            match_data = {'match': link.split('/')[-1], 'games_id': games_id, 'teams': teams, \
                'picks_team_1': round_picks_team1, 'picks_team_2': round_picks_team2, \
                'bans_team_1': round_bans_team1, 'bans_team_2': round_bans_team2, 'durations': duration, \
                'maps': maps_played, 'winners': winner}
            matchs_data.append(match_data)

        print('---- All data gathered ----')
        self.progress.bar_style = 'success'
        

        self.matchs_list = matchs_data
        return self
