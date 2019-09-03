# -*- coding: utf-8 -*-
"""
Other functions:
    Sort/save/display
"""

import pandas as pd
from matplotlib import pyplot as plt
import numpy as np

def dict_to_dataframe(dic):
    """Converts data stored in a dictionnary to a pandas dataframe
    Used for data visualization
    """
    df = pd.DataFrame.from_dict(dic)
    df = df.transpose()
    df.fillna(0, inplace=True)
    return df


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
        ax.annotate(str(list(Played_df[name])[i]), (p.get_x(), p.get_height() * 1.005),
                    fontsize=8, ha='center')
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


def team_stats_subplot(WR_df, Played_df, threshold, ax, name='', team_name='', bans=False):
    """ Subplot for each player
    """
    ## Shaping data for plotting
    WR_df = WR_df.transpose()
    WR_df = WR_df.loc[:, [name]]
    Played_df = Played_df.transpose()
    Played_df = Played_df.loc[:, [name]]
    Played_df, WR_df = quick_played_sort(Played_df, WR_df, name)
    WR_df = WR_df[list(Played_df[name] != 0)]
    Played_df = Played_df[list(Played_df[name] != 0)]

    ## Highlight suggested bans in red: targets heroes overpicked and overperforming.
    ## Margin may be modified to adjust results
    if bans:
        edges_color = ['red' if ban > Played_df[name].mean()*2  else 'black'
                       for ban in Played_df[name]]
        threshold = Played_df[name].mean()
    else:
        plm = Played_df[name].mean()
        wrm = np.average(list(WR_df[name]),
                         weights=(np.asarray(Played_df[name]) / float(sum(Played_df[name]))))
        margin = 1.1
        edges_color = ['red' if Played_df[name][i] > plm*margin and WR_df[name][i] > wrm*margin
                       else 'black' for i in range(0, len(Played_df.index))]

    WR_df[name].plot(ax=ax, kind='bar',
                     color=plt.cm.Blues(Played_df[name]/max(list(Played_df[name]))),
                     edgecolor=edges_color)
    ax.plot([0, len(list(WR_df[name]))], [threshold, threshold], "k--", color='red')

    # add number of picks in text above the bars
    i = 0
    for p in ax.patches:
        ax.annotate(str(list(Played_df[name])[i]), (p.get_x(), p.get_height() * 1.005),
                    fontsize=8, ha='left')
        i += 1
    # add some text for labels, title and axes ticks
    ax.set_ylabel('WR (%)', fontsize=8)
    if bans:
        ax.set_title(team_name+' bans for map: '+name, fontsize=8)
    else:
        ax.set_title(team_name+' winrate by hero: '+name, fontsize=8)
    ax.set_xticklabels(list(WR_df.index), fontsize=8)
