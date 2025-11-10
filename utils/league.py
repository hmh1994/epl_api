from config import LEAGUE_MAP

def map_league_id(web_league_id: str) -> str:
    return LEAGUE_MAP.get(web_league_id.upper(), web_league_id)