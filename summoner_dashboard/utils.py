from datetime import datetime
import requests
import time


# Season Constants
season_start_date = "2023-01-11"
SEASON_START_TIMESTAMP = int(datetime.strptime(season_start_date, "%Y-%m-%d").timestamp())



# API Requests
BURST_LIMIT = 20
BURST_TIME = 1
SUSTAINED_LIMIT = 100
SUSTAINED_TIME = 120

last_request_time = 0

def throttle():
    '''
    Enforces a minimum delay between API requests to prevent exceeding rate limit.
    '''
    global last_request_time
    time_since_last_request = time.time() - last_request_time
    if time_since_last_request < BURST_TIME:
        time.sleep(BURST_TIME - time_since_last_request)
    last_request_time = time.time()


def make_request(url, params):
    '''
    Makes a GET request to the specified URL with the provided parameters.
    
    Parameters:
        url (str): The URL to send the GET request to.
        params (dict): A dictionary of query parameters to include in the GET request.

    Returns:
        dict: The JSON response from the API converted to a dictionary.
    '''
    throttle()
    try:
        response = requests.get(url=url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        if response.status_code == 429:
            retry_after = int(response.headers.get('Retry-After', 1))
            print(f"API rate limit exceeded. Retrying in {retry_after} seconds.")
            time.sleep(retry_after)
            return make_request(url, params)
        else:
            raise Exception(f"Error fetching data from API: {e}")



# Game Type
def get_game_type(queue_id):
    game_types = {
        400: "Normal Draft",
        420: "Ranked Solo",
        430: "Normal Blind",
        440: "Ranked Flex",
        450: "ARAM",
        700: "CLASH",
        830: "Co-op vs AI",
        840: "Co-op vs AI",
        850: "Co-op vs AI",
        900: "URF",
    }
    return game_types.get(queue_id, "Unknown")