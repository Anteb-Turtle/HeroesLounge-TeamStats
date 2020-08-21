import teamclasses as tc
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
        self.team_tag = widgets.Text(tag, description='Team tag:')
        self.team_name = widgets.Text(name, description='Team name:')
        self.seasons = widgets.SelectMultiple(options=[0,1,2,3,4,5,6,7,8,9],
                                        value= n,
                                        description='seasons',
                                        disabled=True)
        button0 = widgets.Button(description="Check team")
        button1 = widgets.Button(description="Submit and run")
        button2 = widgets.Button(description="Display figures")
        self.label = widgets.Label(value='')
        
        self.progress = widgets.IntProgress(value=0, min=0, max=10,bar_style='')
        self.out = widgets.Output()
        
        button0.on_click(self.instantiate)
        button1.on_click(self.submit_input)
        button2.on_click(self.plotter)
        
        display(widgets.HTML(value='<h1 style="font-size:20px;">HeroesLounge-TeamStats Tool</h1>'+
                             '<p>Enter team info and click "Check team", select seasons and click "Submit and run" button. ' +
                             'Wait for the data to be collected from heroes lounge.gg and then click "Display figures".</p>'))
        display(self.team_tag, self.team_name)
        display(button0, self.label, self.seasons)
        display(button1, self.progress)
        display(button2, self.out)
        
    def instantiate(self, *args): 
        ## Called only when the button is pressed
        self.label.value = 'Checking'
        super().__init__(self.team_tag.value, self.team_name.value)
        self.seasons.options = self.seasons_names
        self.seasons.disabled = False
        self.label.value = 'Done'
        
    def submit_input(self, *args):
        ## Called only when the button is pressed
        list_seasons = [self.all_seasons[i] for i,n in enumerate(self.seasons_names) if n in self.seasons.value]
        self.set_seasons(list_seasons)
        ## Import data
        self.gather_online_data()
        ## Process data: convert to dataframes
        self.team_display = tc.TeamDisplayData(raw_data = self.team_data)
        return self.team_display
    
    def plotter(self, *args):
        if hasattr(self, 'team_display'):
            with self.out:
                fig1 = self.players_scatter()
                fig2 = self.maps_scatter()
                fig3 = self.per_player()
                fig4 = self.per_map()
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
        self.progress.max = len(matches_links) - 1
        self.progress.bar_style = ''

        # =============================================================================
        ## Retreive data from each match
        matchs_data = []
        for link in matches_links:
            doc1, games, games_id = self._retreive_link(link)
            self.progress.bar_style = ''
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
            for game in games:
                teams, picks_team1, picks_team2, bans_team1, bans_team2 = self._retreive_game_data(game)
                round_picks_team1.append(picks_team1)
                round_picks_team2.append(picks_team2)
                round_bans_team1.append(bans_team1)
                round_bans_team2.append(bans_team2)

            print('Match data gathered')
            self.progress.value += 1

            duration = doc1.find_all('div', {'class':"col-12 col-md-2"})
            duration = [d.text.split()[1] for d in duration]

            maps_played = doc1.find_all('span', {'class':"badge badge-info"})
            maps_played = [m.text for m in maps_played]

            winner = doc1.findAll('span', {'class':["badge badge-success float-left", "badge badge-success float-right"]})
            winner = [teams[0] if w.get('class')[2] == "float-right" else teams[1] for w in winner]

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
