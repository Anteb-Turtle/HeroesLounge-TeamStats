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
