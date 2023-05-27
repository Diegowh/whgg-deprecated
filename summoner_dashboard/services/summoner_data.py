from .api_handler import APIHandler
from .db_handler import DatabaseHandler
from .match_stats import MatchStats
from .ranked_data import RankedData
from .summoner_info import SummonerInfo


class SummonerData(SummonerInfo, DatabaseHandler, APIHandler, RankedData, MatchStats):
    def __init__(self, summoner_name: str, api_key: str, region: str = "EUW1") -> None:
        self.api_key = api_key
        self.region = region
        self.summoner_name = summoner_name
        self.base_url = f"https://{region}.api.riotgames.com/lol/"
        
        self._summoner_info = None
        self.id = self.summoner_id()
        
        summoner_data = self._summoner_data_from_db()
        
        if summoner_data is not None:
            self.puuid = summoner_data["summoner_puuid"]
            self.icon_id = summoner_data["profile_icon_id"]
            self.level = summoner_data["summoner_level"]
        else:
            self.puuid = self.summoner_puuid()
            self.icon_id = self.summoner_icon_id()
            self.level = self.summoner_level()