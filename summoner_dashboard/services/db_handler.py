from datetime import timedelta
import logging
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from ..models import SummonerModel, MatchModel


logger = logging.getLogger(__name__)
UPDATE_THRESHOLD = timedelta(hours=1)


class DatabaseHandler:
    def _summoner_data_from_db(self) -> dict:
        """Retrieve summoner data from the database based on the summoner_name.
        Returns:
            A dict with summoner data or None if not found.
        """
        try:
            summoner_model = SummonerModel.objects.get(summoner_name=self.summoner_name)
            return {
                "summoner_puuid": summoner_model.summoner_puuid,
                "profile_icon_id": summoner_model.profile_icon_id,
                "summoner_level": summoner_model.summoner_level,
                "soloq_rank": summoner_model.soloq_rank,
                "soloq_lp": summoner_model.soloq_lp,
                "soloq_wins": summoner_model.soloq_wins,
                "soloq_losses": summoner_model.soloq_losses,
                "soloq_wr": summoner_model.soloq_wr,
                "flex_rank": summoner_model.flex_rank,
                "flex_lp": summoner_model.flex_lp,
                "flex_wins": summoner_model.flex_wins,
                "flex_losses": summoner_model.flex_losses,
                "flex_wr": summoner_model.flex_wr,
            }
        
        except SummonerModel.DoesNotExist:
            return None
        
        
    def handle_summoner_data(self, league_data: dict) -> None:
        '''
        Handles the summoner data depending on if the summoner exists in the database
        '''
        
        summoner, created = SummonerModel.objects.get_or_create(summoner_puuid=self.puuid)
        if created:
            self.save_summoner_to_db(league_data)
        
        else:
            self.update_summoner_in_db(league_data, summoner)
        
        
    def update_summoner_in_db(self, league_data: dict, summoner: SummonerModel) -> None:

        current_timestamp = timezone.now()
        
        if current_timestamp - summoner.last_update >= UPDATE_THRESHOLD:
            logger.info("Updating database.")

            summoner.summoner_id = self.id
            summoner.summoner_name = self.summoner_name
            summoner.region = self.region
            summoner.last_update = current_timestamp
            summoner.soloq_rank = league_data["soloq_rank"]
            summoner.soloq_lp = league_data["soloq_lp"]
            summoner.soloq_wins = league_data["soloq_wins"]
            summoner.soloq_losses = league_data["soloq_losses"]
            summoner.soloq_wr = league_data["soloq_wr"]
            summoner.flex_rank = league_data["flex_rank"]
            summoner.flex_lp = league_data["flex_lp"]
            summoner.flex_wins = league_data["flex_wins"]
            summoner.flex_losses = league_data["flex_losses"]
            summoner.flex_wr = league_data["flex_wr"]
            summoner.profile_icon_id = self.icon_id
            summoner.summoner_level = self.level

            summoner.save()
                
        else:
            logger.info("Summoner data is up-to-date.")
        
    
    def save_summoner_to_db(self, league_data: dict) -> None:
        current_timestamp = timezone.now()
        
        logger.info("Adding a new summoner to the database.")
        SummonerModel.objects.create(
            summoner_puuid=self.puuid,
            summoner_id=self.id,
            summoner_name=self.summoner_name,
            region=self.region,
            last_update=current_timestamp,
            soloq_rank=league_data["soloq_rank"],
            soloq_lp=league_data["soloq_lp"],
            soloq_wins=league_data["soloq_wins"],
            soloq_losses=league_data["soloq_losses"],
            soloq_wr=league_data["soloq_wr"],
            flex_rank=league_data["flex_rank"],
            flex_lp=league_data["flex_lp"],
            flex_wins=league_data["flex_wins"],
            flex_losses=league_data["flex_losses"],
            flex_wr=league_data["flex_wr"],
            profile_icon_id=self.icon_id,
            summoner_level=self.level,
        )
            
            
    def _matches_data_from_db(self) -> list[dict]:
        try:
            last_match = self._get_last_match()
            
            if last_match:
                self._handle_new_matches(last_match)
        
            else:
                self._handle_all_matches()
            
            return self._get_all_match_data()
        
        except ObjectDoesNotExist:
            logger.warning("No matches found for summoner.")
            return []
        

    def _get_last_match(self):
        return MatchModel.objects.filter(summoner_puuid=self.puuid).order_by('-match_id').first()
    
    
    def _handle_new_matches(self, last_match):
        recent_matches = [
            match_id for match_id in self.all_match_ids_this_season() if match_id > last_match.match_id
        ]
        if recent_matches:
            logger.info("Found new matches, updating database...")
            new_matches_data = self._matches_data(recent_matches)
            self.save_matches_data_to_db(new_matches_data)
            
    
    def _handle_all_matches(self):
        all_matches = self.all_match_ids_this_season()
        if all_matches:
            logger.info("Adding all matches to the database...")
            all_matches_data = self._matches_data(all_matches)
            self.save_matches_data_to_db(all_matches_data)
            
            
    def _get_all_match_data(self):
        matches = MatchModel.objects.filter(summoner__summoner_puuid=self.puuid).select_related('summoner')
        matches_data = []

        for match in matches:
            match_data = {
                    "summoner_puuid": match.summoner.summoner_puuid,
                    "match_id": match.match_id,
                    "champion_name": match.champion_name,
                    "win": match.win,
                    "kills": match.kills,
                    "deaths": match.deaths,
                    "assists": match.assists,
                    "kda": match.kda,
                    "cs": match.cs,
                    "vision": match.vision,
                    "summoner_spell1": match.summoner_spell1,
                    "summoner_spell2": match.summoner_spell2,
                    "item0": match.item0,
                    "item1": match.item1,
                    "item2": match.item2,
                    "item3": match.item3,
                    "item4": match.item4,
                    "item5": match.item5,
                    "item6": match.item6,
                    "participant1_summoner_name": match.participant_summoner_names[0],
                    "participant2_summoner_name": match.participant_summoner_names[1],
                    "participant3_summoner_name": match.participant_summoner_names[2],
                    "participant4_summoner_name": match.participant_summoner_names[3],
                    "participant5_summoner_name": match.participant_summoner_names[4],
                    "participant6_summoner_name": match.participant_summoner_names[5],
                    "participant7_summoner_name": match.participant_summoner_names[6],
                    "participant8_summoner_name": match.participant_summoner_names[7],
                    "participant9_summoner_name": match.participant_summoner_names[8],
                    "participant10_summoner_name": match.participant_summoner_names[9],
                    "participant1_champion_name": match.participant_champion_names[0],
                    "participant2_champion_name": match.participant_champion_names[1],
                    "participant3_champion_name": match.participant_champion_names[2],
                    "participant4_champion_name": match.participant_champion_names[3],
                    "participant5_champion_name": match.participant_champion_names[4],
                    "participant6_champion_name": match.participant_champion_names[5],
                    "participant7_champion_name": match.participant_champion_names[6],
                    "participant8_champion_name": match.participant_champion_names[7],
                    "participant9_champion_name": match.participant_champion_names[8],
                    "participant10_champion_name": match.participant_champion_names[9],
                    "participant1_team_id": match.participant_team_ids[0],
                    "participant2_team_id": match.participant_team_ids[1],
                    "participant3_team_id": match.participant_team_ids[2],
                    "participant4_team_id": match.participant_team_ids[3],
                    "participant5_team_id": match.participant_team_ids[4],
                    "participant6_team_id": match.participant_team_ids[5],
                    "participant7_team_id": match.participant_team_ids[6],
                    "participant8_team_id": match.participant_team_ids[7],
                    "participant9_team_id": match.participant_team_ids[8],
                    "participant10_team_id": match.participant_team_ids[9],
                    "game_mode": match.game_mode,
                    "game_duration": match.game_duration,
                    "queue_id": match.queue_id,
                    "team_position": match.team_position,
                }
            matches_data.append(match_data)
        logger.info("Retrieved all match data.")
        return matches_data