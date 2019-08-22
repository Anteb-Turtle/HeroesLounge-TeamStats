# -*- coding: utf-8 -*-
"""
Created on Thu Aug 22 10:24:48 2019

@author: antoine.bierret
"""

import json
import pandas as pd
import requests
from bs4 import BeautifulSoup as soup
from matplotlib import pyplot as plt
import supportfunctions as fun
import formatdata as fd
import test_3classes as tc

team_name = 'Nimemuona'
team_tag =  'Nimemuona'

team_data = tc.TeamRawData(team_tag, team_name)
team_data.set_seasons([0,1,2])
team_data.load_from_json('test.json')

team_processed = tc.TeamProcessedData(team_data)

team_display = tc.TeamDisplayData(processed_data = team_processed)

