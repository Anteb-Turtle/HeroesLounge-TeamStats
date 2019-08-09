# -*- coding: utf-8 -*-
"""
Other functions:
    Sort/save/display
"""

import pandas as pd
from matplotlib import pyplot as plt


def dict_to_dataframe(dic):
    """Converts data stored in a dictionnary to a pandas dataframe
    Used for data visualization
    """
    df = pd.DataFrame.from_dict(dic)
    df = df.transpose()
    df.fillna(0, inplace=True)
    return df


def save_to_excel(file_name, list_of_df, list_of_datatypes):
    """Save all dataframes to an excel file
    """
    # Create a Pandas Excel writer using XlsxWriter
    writer = pd.ExcelWriter(file_name+'.xlsx', engine='xlsxwriter')
    i = 0
    for df in list_of_df:
        # Convert the dataframe to an XlsxWriter Excel object
        df.to_excel(writer, sheet_name=list_of_datatypes[i])
        i += 1

    writer.save()
    print('Data saved to: '+file_name+'.xlsx')


def display_indiv_stats(WR_df, Played_df, name='', team_name=''):
    """ Displays a bar plot of heroes WR and number played for a player or a map
    """
    WR_df = WR_df.transpose()
    WR_df = WR_df.loc[:, [name]]
    Played_df = Played_df.transpose()
    Played_df = Played_df.loc[:, [name]]
    Played_df, WR_df = quick_played_sort(Played_df, WR_df, name)
    WR_df = WR_df[list(Played_df[name] != 0)]
    Played_df = Played_df[list(Played_df[name] != 0)]

    fig, ax = plt.subplots()
    WR_df[name].plot(ax=ax, kind='bar')
    i = 0
    for p in ax.patches:
        ax.annotate(str(list(Played_df[name])[i]), (p.get_x(), p.get_height() * 1.005), fontsize=8, ha='center')
        i += 1
    # add some text for labels, title and axes ticks
    ax.set_ylabel('WR (%)')
    ax.set_title(team_name+' winrate by hero: '+name)
    ax.set_xticklabels(list(WR_df.index), fontsize=8)

    plt.show()


def sort_by_most_played(df_m_p, df_m_wr, df_p_p, df_p_wr):
    """ Sorts the datframes so that the most played maps/heroes are in the first rows
    """
    df_m_p['tot'] = df_m_p.sum(axis=1)
    df_p_p['tot'] = df_p_p.sum(axis=1)
    df_m_wr['tot'] = df_m_p.sum(axis=1)
    df_p_wr['tot'] = df_p_p.sum(axis=1)
    df_m_p = df_m_p.sort_values(by='tot', axis=0, ascending=False)
    df_m_p.drop('tot', axis=1, inplace=True)
    df_p_p = df_p_p.sort_values(by='tot', axis=0, ascending=False)
    df_p_p.drop('tot', axis=1, inplace=True)
    df_m_wr = df_m_wr.sort_values(by='tot', axis=0, ascending=False)
    df_m_wr.drop('tot', axis=1, inplace=True)
    df_p_wr = df_p_wr.sort_values(by='tot', axis=0, ascending=False)
    df_p_wr.drop('tot', axis=1, inplace=True)
    return df_m_p, df_m_wr, df_p_p, df_p_wr

def quick_played_sort(df_p, df_wr, col_name):
    """ Sort dataframe for easier visualization
    """
    df_p.rename(columns={col_name: 'sort'}, inplace=True)
    df_wr = pd.concat([df_wr, df_p], axis=1)
    df_wr = df_wr.sort_values(by='sort', axis=0, ascending=False)
    df_wr.drop('sort', axis=1, inplace=True)
    df_p = df_p.sort_values(by='sort', axis=0, ascending=False)
    df_p.rename(columns={'sort': col_name}, inplace=True)

    return df_p, df_wr


def display_team_stats(WR_df, Played_df, team_wr, max_player=5, team_name=''):
    """ Displays a bar plot of heroes WR and number played for first max_players players in a team
    """
#    ax=[None]*6
#    fig, ((ax[0],ax[1],ax[2]),(ax[3],ax[4],ax[5])) = plt.subplots(2,3)
    n_lines = (max_player-1)//3+1
    fig, ax = plt.subplots(n_lines, 3)
    i = 0
    for player in list(WR_df.iloc[0:max_player, :].index):
        if n_lines > 1:
            team_stats_subplot(WR_df, Played_df, team_wr, ax[i//3, i%3], name=player, team_name=team_name)
        else:
            team_stats_subplot(WR_df, Played_df, team_wr, ax[i], name=player, team_name=team_name)
        i += 1

    plt.tight_layout()
    plt.show()


def team_stats_subplot(WR_df, Played_df, threshold, ax, name='', team_name=''):
    """ Subplot for each player
    """

    WR_df = WR_df.transpose()
    WR_df = WR_df.loc[:, [name]]
    Played_df = Played_df.transpose()
    Played_df = Played_df.loc[:, [name]]
    Played_df, WR_df = quick_played_sort(Played_df, WR_df, name)
    WR_df = WR_df[list(Played_df[name] != 0)]
    Played_df = Played_df[list(Played_df[name] != 0)]

    WR_df[name].plot(ax=ax, kind='bar')
    ax.plot([0, len(list(WR_df[name]))], [threshold, threshold], "k--", color='red')
    i = 0
    for p in ax.patches:
        ax.annotate(str(list(Played_df[name])[i]), (p.get_x(), p.get_height() * 1.005), fontsize=8, ha='left')
        i += 1
    # add some text for labels, title and axes ticks
    ax.set_ylabel('WR (%)', fontsize=8)
    ax.set_title(team_name+' winrate by hero: '+name, fontsize=8)
    ax.set_xticklabels(list(WR_df.index), fontsize=8)


def display_map_stats(WR_df, Played_df, threshold_df, team_name=''):
    """ Displays a bar plot of heroes WR and number played for a player or a map
    """
    N = len(Played_df.index)
    ax = [None]*9
    fig, ((ax[0], ax[1], ax[2]), (ax[3], ax[4], ax[5]), (ax[6], ax[7], ax[8])) = plt.subplots(3,3)
    i = 0
    for maps in list(WR_df.iloc[0:N, :].index):
        team_stats_subplot(WR_df, Played_df, threshold_df.loc[maps, :], ax[i], name=maps, team_name=team_name)
        i += 1

    plt.tight_layout()
    plt.show()
