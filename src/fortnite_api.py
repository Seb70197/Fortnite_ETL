import requests
import pandas as pd
import datetime as dt
from datetime import date
import time
import numpy as np
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
    
    header_api = api_cred()
    dict_epic_id = dict(zip(players_df['player_id'], players_df['platform']))
    
    player_stats = pd.DataFrame()
    #Create blank data list to store Stats inside
    data = []

    #Loop the player's stats and saved them in the list
    for key, value in dict_epic_id.items():
        url_player_stats = f'https://fortnite-api.com/v2/stats/br/v2?name={key}&accountType={value}'       
        response_player_stat = requests.get(url_player_stats, headers = header_api)
        #Manage potential errors in the API call
        if response_player_stat.status_code != 200:
            print(f"Error fetching data for player {key}: {response_player_stat.status_code}")
            continue
        
        time.sleep(1)  #To avoid hitting the API rate limit

        data_json_stats = response_player_stat.json()
        stats = pd.DataFrame(data_json_stats['data']['stats']['all']).T
        stats = stats[['wins','kd','winRate','top3','top5','top6','top10','top12','top25','kills','matches','minutesPlayed','score','playersOutlived','lastModified']]
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
        'players_outlived']].fillna(0).astype(int)
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
    #the fortnite-api.com includes 'ltm' stats that we don't want to keep
    players_stats_current = players_stats_current.loc[players_stats_current['type_party']!='ltm']
    players_stats_current = players_stats_current.loc[players_stats_current['type_party']!='overall']


    return players_stats_current

def clean_upload_stats(players_stats_hist, players_stats_current):
    #From the historical stats, keep only the necessary columns and the latest update (not the evo stats)
    players_stats_hist_update = players_stats_hist.iloc[:, np.r_[0:2,20:len(players_stats_hist.columns)]].copy()
    players_stats_current_update = players_stats_current.copy()

    # players_stats_hist = players_stats_hist.loc[players_stats_hist['update_date'] == players_stats_hist['update_date'].max()]
    #Remove the '_value' suffix from the historical stats columns to merge properly
    players_stats_hist_update.columns = players_stats_hist_update.columns.str.replace('_value','')

    #Create an ID column to merge both dataframes
    players_stats_hist_update['ID'] = players_stats_hist_update['type_party']+'-'+players_stats_hist_update['player_id']
    #players_stats_current_update['ID'] = players_stats_current_update['index']+'-'+players_stats_current_update['player_id']

    #Define columns to calculate evolution (remove the one for which evolution is not relevant)
    stats_columns = ['score', 'top_1', 'top_3', 'top_5', 'top_6', 'top_10', 'top_12',
            'top_25', 'kill_death', 'win_rate', 'match_played', 'kills', 'min_played', 'kills_per_min', 'kills_per_match', 'score_per_match', 'score_per_min', 'players_outlived']

    #Calculate the evolution by subtracting current stats with historical stats
    players_stats_current_update = players_stats_current.set_index('ID')[stats_columns].subtract(players_stats_hist_update.set_index('ID')[stats_columns])
    #Merge the evolution stats with the current stats to have both in the same dataframe
    players_stats_current_update = players_stats_current_update.merge(players_stats_current, on='ID', suffixes=('_evo','_value'))

    #Reorder columns of the dataframe before uploading to the SQL Table
    players_columns_order = ['type_party', 'player_id', 'score_evo', 'top_1_evo', 'top_3_evo','top_5_evo', 'top_6_evo', 'top_10_evo', 'top_12_evo', 'top_25_evo',
        'kill_death_evo', 'win_rate_evo', 'match_played_evo', 'kills_evo','min_played_evo', 'kills_per_min_evo', 'kills_per_match_evo','score_per_min_evo', 
        'score_per_match_evo', 'players_outlived_evo','score_value', 'top_1_value', 'top_3_value', 'top_5_value','top_6_value', 'top_10_value', 'top_12_value', 
        'top_25_value','kill_death_value', 'win_rate_value', 'match_played_value','kills_value', 'min_played_value', 'kills_per_min_value',
        'kills_per_match_value', 'score_per_min_value', 'score_per_match_value', 'players_outlived_value', 'update_date']

    players_stats_current_update = players_stats_current_update[players_columns_order]

    return players_stats_current_update

