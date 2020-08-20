# -*- coding: utf-8 -*-
"""
Created on Thu Aug 20 10:00:11 2020

@author: antoine.bierret
"""

import teamclasses as tc
import ipywidgets as widgets
from ipywidgets import interact, interact_manual, interactive
from IPython.display import display
import plotly.express as px
import pandas as pd
import numpy as np

class TeamWidget():
    
    def __init__(self, tag = 'Turtles', name='Turtle Team', n = [0]):
        ## Set the widgets and display them
        self.team_tag = widgets.Text(tag, description='Team tag:')
        self.team_name = widgets.Text(name, description='Team name:')
        self.seasons = widgets.SelectMultiple(options=[0,1,2,3,4,5,6,7,8,9],
                                        value= n,
                                        description='seasons',
                                        disabled=False)
        button = widgets.Button(description="Submit and run")
        button.on_click(self.submit_input)
        display(self.team_tag, self.team_name, self.seasons, button)
        
    def submit_input(self, *args):
        ## Called only when the button is pressed
        team_data = tc.TeamRawData(self.team_tag.value, self.team_name.value)
        team_data.set_seasons(list(self.seasons.value))
        ## Import data
        team_data.gather_online_data()
        ## Process data: convert to dataframes
        self.team_display = tc.TeamDisplayData(raw_data = team_data)
        return self.team_display


    
class DisplayWidget():
    def __init__(self, team_display, ):
        self.team_display = team_display
        
        children = [self.players_scatter(), self.maps_scatter()]
        tab = widgets.Tab()
        tab.children = children
        tab.titles = ['Stats for all players', 'Stats for all maps']
        display(tab)
                
        
    
    def players_scatter(self):
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
        
    def maps_scatter(self):   
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
    
    def players_hist(self):
        disp1 = pd.melt(self.team_display.df_player_wr.reset_index(), id_vars=['index'], var_name='hero', value_name='WR')
        disp2 = pd.melt(self.team_display.df_player_played.reset_index(), id_vars=['index'], var_name='hero', value_name='played')
        disp = pd.merge(disp1,disp2, how='outer')
        disp = disp.fillna(0)
        #plotting
        fig = px.scatter(disp, x='hero', y='index', size='played', color='WR')
        fig.show()
        return fig

    def per_map(self):
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
        
        
     
        
        
