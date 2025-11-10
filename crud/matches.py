from database import execute_raw

async def get_match_schedule(db, league_id: str, season: str, matchweek: int = None):
    query = """
        SELECT f.id AS fixture_id, f.game_week, f.kickoff_time, f.home_team_id, f.away_team_id
        FROM fixtures f
        LEFT JOIN seasons s ON f.season_id = s.id
        LEFT JOIN competitions c ON s.competition_id = c.id
        WHERE c.abbreviation = :league_id AND s.abbreviation = :season
    """
    params = {"league_id": league_id, "season": season}
    if matchweek:
        query += " AND f.game_week = :matchweek"
        params["matchweek"] = matchweek
    return execute_raw(db, query, params)

async def get_match_detail(db, match_id: str):
    query = """
        SELECT m.*, h.name_en AS home_team, a.name_en AS away_team
        FROM matches m
        LEFT JOIN teams h ON m.home_team_id = h.id
        LEFT JOIN teams a ON m.away_team_id = a.id
        WHERE m.id = :match_id
    """
    return execute_raw(db, query, {"match_id": match_id})
