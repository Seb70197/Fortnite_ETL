import requests
import pandas as pd
import datetime as dt
from datetime import date
import os


def api_cred():

    type_api = os.environ['HEADER_API_TYPE']
    value_api = os.environ['HEADER_API_VALUE']
    header_api = {type_api: value_api}

    return header_api


def find_epic_id(player_id):
    """Find a player Epic ID according to his display name

    Args:
        player_id (str): The display name of the player.

    Returns:
        str: The Epic ID of the player if found, otherwise None.
    """
    #get the epi credentials for API Access
    header_api = api_cred()

    #API address to get Epic ID from display name
    url_user_id = 'https://fortniteapi.io/v1/lookup?username='
    #API Call to get Epic ID
    response_user_ID = requests.get(url_user_id+str(player_id), headers = header_api)
    #Limit the response to only the account_id
    epic_id = response_user_ID.json().get('account_id')
    #Manage cases where Epic ID is not found
    if epic_id is not None:
        return epic_id
    else:
        return print("Epic ID not found")
    
def get_stats(players_df):
    dict_epic_id = dict(zip(players_df['player_id'], players_df['epic_id']))
    url_player_stats = 'https://fortniteapi.io/v1/stats?account='

    player_stats = pd.DataFrame()
    #Create blank data list to store Stats insis
    data = []

    #Loop the player's stats and saved them in the list
    for key, value in dict_epic_id.items():
        response_player_stat = requests.get(url_player_stats+str(value), headers = api_cred())
        data_json_stats = response_player_stat.json()
        stats = pd.DataFrame(data_json_stats.get('global_stats')).T
        stats = stats[['placetop1', 'kd', 'winrate','placetop3','placetop5', 'placetop6','placetop10', 'placetop12', 'placetop25', 'kills','matchesplayed', 'minutesplayed', 'score', 'playersoutlived', 'lastmodified']]
        stats.columns = ['top_1', 'kill_death', 'win_rate','top_3','top_5', 'top_6','top_10', 'top_12', 'top_25', 'kills','match_played', 'min_played', 'score', 'players_outlived', 'last_modified']
        stats['player_id'] = key
        data.append(stats)

    for i in range(len(data)):
        player_stats = pd.concat([player_stats, data[i]])
    player_stats.drop(['last_modified'], axis='columns', inplace=True)

    return player_stats

def clean_current_stats(players_stats_current):

    #avatar_dict = dict(zip(players_df['player_id'], players_df['avatar_url']))

    #Set the columns as int where necessary
    players_stats_current[['top_1', 'top_3', 'top_5', 'top_6', 'top_10',
        'top_12', 'top_25', 'kills', 'match_played', 'min_played', 'score',
        'players_outlived']] = players_stats_current[['top_1', 'top_3', 'top_5', 'top_6', 'top_10',
        'top_12', 'top_25', 'kills', 'match_played', 'min_played', 'score',
        'players_outlived']].astype(int)
    #Reorder columns
    players_stats_current = players_stats_current[['player_id', 'top_1', 'top_3', 'top_5', 'top_6', 'top_10',
        'top_12', 'top_25', 'kills', 'kill_death', 'win_rate','match_played', 'min_played', 'score',
        'players_outlived']]
    #rename column to Match Played
    players_stats_current = players_stats_current.rename(columns={'Match Player':'Match Played'})

    #Create a column containing the update's date
    today = date.today()
    players_stats_current['update_date'] = today

    #Add additional Statistics
    players_stats_current['kills_per_match'] = players_stats_current['kills']/players_stats_current['match_played']
    players_stats_current['kills_per_min'] = players_stats_current['kills']/players_stats_current['min_played']
    players_stats_current['score_per_match'] = players_stats_current['score']/players_stats_current['match_played']
    players_stats_current['score_per_min'] = players_stats_current['score']/players_stats_current['min_played']
    players_stats_current = players_stats_current.reset_index()
    players_stats_current.rename(columns={'index': 'type_party'}, inplace=True)
    players_stats_current['ID'] = players_stats_current['type_party']+'-'+players_stats_current['player_id']

    return players_stats_current

