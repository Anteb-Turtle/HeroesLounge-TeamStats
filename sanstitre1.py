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
import matplotlib.pyplot as plt

class TeamWidget():
    
    def __init__(self, tag = 'TT', name='Turtle Team', n = [0]):
        print('init')
        self.team_tag = widgets.Text(tag)
        self.team_name = widgets.Text(name)
        self.seasons = widgets.SelectMultiple(options=[0,1,2,3,4,5,6,7,8,9],
                                        value= n,
                                        description='seasons',
                                        disabled=False)
        button = widgets.Button(description="Submit and run")
        button.on_click(self.submit_input())
        display(self.team_tag, self.team_name, self.seasons, button)
        print('display')
        
    def submit_input(self):
        print('click')
        team_data = tc.TeamRawData(self.team_tag, self.team_name)
        team_data.set_seasons(self.seasons)
        ## Import data
        team_data.gather_online_data()
        ## Process data: convert to dataframes
        self.team_display = tc.TeamDisplayData(raw_data = team_data)
        return self.team_display
