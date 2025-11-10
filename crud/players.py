from database import execute_raw

async def get_player_database(db, league_id: str, season: str, team_id: str = None):
    query = """
        SELECT p.id, p.display_name_en AS name, p.position, p.photo_url AS avatar,
               ps.appearances::int AS appearances, ps.shooting_goals::int AS goals,
               ps.passing_assists::int AS assists, ps.shooting_expected_goals::float AS xG
        FROM players p
        LEFT JOIN player_stats ps ON p.id = ps.player_id
        LEFT JOIN seasons s ON ps.season_id = s.id
        LEFT JOIN competitions c ON s.competition_id = c.id
        WHERE s.abbreviation = :season
    """
    params = {"season": season}
    if league_id:
        query += " AND c.abbreviation = :league_id"
        params["league_id"] = league_id
    if team_id:
        query += " AND ps.team_id = :team_id"
        params["team_id"] = team_id
    return execute_raw(db, query, params)
