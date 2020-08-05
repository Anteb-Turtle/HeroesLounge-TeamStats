import plotly.express as px

#Tidying dataframe
disp1 = pd.melt(team_display.df_map_wr.reset_index(), id_vars=['index'], var_name='hero', value_name='WR')
disp2 = pd.melt(team_display.df_map_played.reset_index(), id_vars=['index'], var_name='hero', value_name='played')
disp3 = pd.melt(team_display.df_bans_map.reset_index(), id_vars=['index'], var_name='hero', value_name='banned')
disp = pd.merge(pd.merge(disp1,disp2, how='outer'),disp3, how='outer')
disp = disp.fillna(0)
disp.groupby(by=['index','hero'], as_index=False).sum()
disp['ocurence'] = disp['played'] + disp['banned']
disp = disp[disp.played != 0]

#plotting
fig = px.scatter(disp, x='hero', y='index', size='ocurence', color='WR')
fig.show()


disp1 = pd.melt(team_display.df_player_wr.reset_index(), id_vars=['index'], var_name='hero', value_name='WR')
disp2 = pd.melt(team_display.df_player_played.reset_index(), id_vars=['index'], var_name='hero', value_name='played')
disp = pd.merge(disp1,disp2, how='outer')
disp = disp.fillna(0)
#disp.groupby(by=['index','hero'], as_index=False).sum()
#disp = disp[disp.played != 0]

#plotting
fig = px.scatter(disp, x='hero', y='index', size='played', color='WR')
fig.show()

import numpy as np

tidy_players = (team_display.df_player_wr * team_display.df_player_played).sum(axis=0)
tidy_players = pd.concat([tidy_players, team_display.df_player_played.sum(axis=0)], axis=1)
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
      yref= 'y', y0= team_display.team_winrate, y1= team_display.team_winrate,
      xref= 'x', x0= 0, x1= max(tidy_players.played+1)
    )
])
fig.show()
