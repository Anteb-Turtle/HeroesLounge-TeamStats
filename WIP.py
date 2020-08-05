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


tidy_players = (team_display.df_player_wr * team_display.df_player_played).sum(axis=0)
tidy_players = pd.concat([tidy_players, team_display.df_player_played.sum(axis=0)], axis=1)
tidy_players.columns = ['WR', 'played']
tidy_players['WR'] = tidy_players['WR'] / tidy_players['played']
tidy_players.reset_index(inplace=True)

# Shifting annotations
shift = [(0,0), (5,0),(-5,0),(0,5),(0,-5)]
tidy_players = tidy_players.sort_values(by=['WR','played'])
tidy_players['shift'] = [shift[0]]*len(tidy_players.index)
for ind in range(1, len(tidy_players.index)+1):
    if tidy_players.iloc[ind,1:4] == tidy_players.iloc[ind-1,1:4]
    
 
fig = px.scatter(tidy_players, x='played', y='WR', color='WR', size='played')
for index, row in tidy_players.iterrows():
    fig.add_annotation(dict(x=row['played'],
                   y=row['WR'],
                   showarrow=False,
                   text=row['index'],
                    yanchor='bottom',
                   xshift=,
                    yshift=,
                   xref="x",
                   yref="y"))
fig.show()
