from ..models import ChampionStatsModel, MatchModel
from django.db.models import F
from typing import List
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Count, Sum, Avg, F, FloatField, ExpressionWrapper
from django.db.models import OuterRef, Exists


RECENT_MATCHES_LIMIT = 10
TOP_CHAMPIONS_LIMIT = 5

class MatchStats:
    def recent_matches_data(self) -> List[dict]:
        matches_data = self._matches_data_from_db()
        self.update_champion_stats()

        if not matches_data:
            return []
        
        def match_id_key(match_data):
            return match_data.match_id

        matches_data.sort(key=match_id_key, reverse=True)
        recent_matches_data = matches_data[:RECENT_MATCHES_LIMIT]

        return recent_matches_data
    
    
    def update_champion_stats(self):
        matches = MatchModel.objects.values(
            'summoner',
            'champion_name'
        ).filter(
            queue_id__in= [420, 440] # Filtro para obtener solo los datos de soloq y flex
        ).annotate(
            matches_played= Count('match_id'),
            wins= Sum('win'),
            losses= ExpressionWrapper(Count('match_id') - Sum('win'), output_field=FloatField()),
            wr= ExpressionWrapper(Sum('win') * 100.0 / Count('match_id'), output_field=FloatField()),
            kda= ExpressionWrapper((Sum('kills') + Sum('assists')) / (Sum('deaths') + 0.001), output_field=FloatField()),
            kills= Avg('kills'),
            deaths= Avg('deaths'),
            assists= Avg('assists'),
            cs= Avg('cs')
        )
        
        for match in matches:
            defaults = {
                'matches_played': match['matches_played'],
                'wins': match['wins'],
                'losses': match['losses'],
                'wr': match['wr'],
                'kda': match['kda'],
                'kills': match['kills'],
                'deaths': match['deaths'],
                'assists': match['assists'],
                'cs': match['cs']
            }
            ChampionStatsModel.objects.update_or_create(
                summoner_id= match['summoner'],
                champion_name= match['champion_name'],
                defaults= defaults
            )
        
    def top_champions_data(self, top=TOP_CHAMPIONS_LIMIT):
        top_champions = ChampionStatsModel.objects.filter(
            summoner_id= self.puuid
        ).order_by(
            F('matches_played').desc(),
            F('wr').desc(),
            F('kda').desc(),
        )[:top]
        
        # Convierto a lista directamente los values de top_champions
        top_champions_list = list(top_champions.values(
            "champion_name",
            "matches_played",
            "wr",
            "kda",
            "kills",
            "deaths",
            "assists",
            "cs"
        ))
        
        return top_champions_list
        
    def role_data(self) -> dict:
        roles = ["TOP", "JUNGLE", "MIDDLE", "BOTTOM", "UTILITY"]
        
        role_counts = {role: 0 for role in roles}
        
        role_data = MatchModel.objects.values('team_position').filter(summoner__summoner_puuid=self.puuid)
        
        # Cuento la frecuencia de cada rol
        role_frequencies = role_data.annotate(count=Count('team_position')).values('team_position', 'count')
        
        # Actualizo el diccionario de role_counts
        for role in role_frequencies:
            role_counts[role['team_position']] = role['count']
                
        return role_counts