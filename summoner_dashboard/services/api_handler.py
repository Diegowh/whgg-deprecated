from typing import Dict, Any
from urllib.parse import urlunparse

from ..utils import make_request, SEASON_START_TIMESTAMP



class APIHandler:
    def _get(self, endpoint, general_region=False, **params) -> Dict[str, Any] :
        '''
        Private method that performs a GET request to the specified Riot API endpoint.
        '''
        region_url = "europe" if general_region else self.region
        
        # Utilizo urlunparse para construir la URL
        netloc = f"{region_url}.api.riotgames.com"
        path = f"lol/{endpoint}"
        url = urlunparse(('https', netloc, path, '', '', ''))
        
        params['api_key'] = self.api_key
        
        try:
            return make_request(url, params)
        except Exception as e:
            raise Exception(f"Error fetching data from API: {e}")
        
    def all_match_ids_this_season(self) -> list:
        '''
        Devuelve todos los match id de las partidas jugadas.
        '''
        MAX_GAMES = 5000
        REQUEST_CAP = 100
        match_ids = []
        
        for start_index in range(0, MAX_GAMES, REQUEST_CAP):
            endpoint = f"match/v5/matches/by-puuid/{self.puuid}/ids"
            params = {
                "startTime": SEASON_START_TIMESTAMP,
                "start": start_index,
                "count": int(min(REQUEST_CAP, MAX_GAMES - start_index))
            }
            current_match_ids = self._get(endpoint, general_region=True, **params)
            
            if not current_match_ids:
                break
            
            match_ids += current_match_ids
            
        return match_ids
    
    
    def _handle_participant_data(self, participant) -> dict:
        return {
            "summoner_name": participant["summonerName"],
            "champion_name": participant["championName"],
            "team_id": participant["teamId"],
        }
    
    
    def _handle_summoner_data(self, participant) -> dict:
        return {
            "summoner_puuid": self.puuid,
            "champion_name": participant["championName"],
            "kills": participant["kills"],
            "deaths": participant["deaths"],
            "assists": participant["assists"],
            "win": 1 if participant["win"] else 0,
            "kda": self.calculate_kda(participant["kills"], participant["deaths"], participant["assists"]),
            "cs": participant["totalMinionsKilled"] + participant["neutralMinionsKilled"],
            "vision": participant["visionScore"],
            "summoner_spell1": participant["summoner1Id"],
            "summoner_spell2": participant["summoner2Id"],
            "item0": participant["item0"],
            "item1": participant["item1"],
            "item2": participant["item2"],
            "item3": participant["item3"],
            "item4": participant["item4"],
            "item5": participant["item5"],
            "item6": participant["item6"],
            "team_position": participant["teamPosition"],
        }
    
    
    def _handle_match_data(self, match_request) -> dict:
        return {
            "game_mode": match_request["info"]["gameMode"],
            "game_duration": match_request["info"]["gameDuration"],
            "queue_id": match_request["info"]["queueId"]
        }
    
    
    def _matches_data(self, match_ids: list = None) -> dict:    
        """
        Devuelve un diccionario con los datos del summoner y los datos de todos los participantes para cada match_id.
        """
        if match_ids is None:
            match_ids = self.all_match_ids_this_season()
            
        all_matches_data = {}
        
        for match_id in match_ids:
            endpoint = f"match/v5/matches/{match_id}"
            try:
                match_request = self._get(general_region=True, endpoint=endpoint)
            except Exception as e:
                print(f"Error getting data for match_id {match_id}: {e}")
                continue
            
            # Manejo la posibilidad de que haya cambiado el formato de los datos dispuesto por la API de Riot Games
            if "info" not in match_request or "participants" not in match_request["info"]:
                print(f"Unexpected format of data for match_id {match_id}: {match_request}")
                continue
        
            summoner_data = None
            participants_data = []


            for participant in match_request["info"]["participants"]:
                participant_info = self._handle_participant_data(participant)
                participants_data.append(participant_info)
                
                if participant["puuid"] == self.puuid:
                    summoner_data = self._handle_summoner_data(participant)
                    
            if summoner_data is None:
                print(f"No summoner data found for match_id {match_id} and puuid {self.puuid}")
                continue
            
            
            match_data = self._handle_match_data(match_request)
            
            all_match_data= {
                "match_data": match_data,
                "summoner_data": summoner_data,
                "participants_data": participants_data,
            }
            all_matches_data[match_id] = all_match_data
        
        return all_matches_data