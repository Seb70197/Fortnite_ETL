import requests
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