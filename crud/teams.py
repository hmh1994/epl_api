from database import execute_raw

async def get_teams(db, league_id: str = None, search: str = None):
    query = """
        SELECT t.id, t.name_en, t.short_name_en, t.icon_url
        FROM teams t
        LEFT JOIN team_stats ts ON t.id = ts.team_id
        LEFT JOIN seasons s ON ts.season_id = s.id
        LEFT JOIN competitions c ON s.competition_id = c.id
        WHERE 1=1
    """
    params = {}
    if league_id:
        query += " AND c.abbreviation = :league_id"
        params["league_id"] = league_id
    if search:
        query += " AND (t.name_en ILIKE :search OR t.short_name_en ILIKE :search)"
        params["search"] = f"%{search}%"
    rows = execute_raw(db, query, params)
    return [
        {
            "id": r["id"],
            "name": r["name_en"],
            "shortName": r["short_name_en"],
            "crest": r["icon_url"],
        }
        for r in rows
    ]

async def get_team_squad(db, team_id: str, season: str):
    query = """
        SELECT p.id, p.display_name_en, p.position, p.photo_url, p.birth_date, p.nationality_en,
               ps.appearances::int AS appearances, ps.shooting_goals::int AS goals,
               ps.passing_assists::int AS assists
        FROM players p
        LEFT JOIN player_stats ps ON p.id = ps.player_id
        LEFT JOIN seasons s ON ps.season_id = s.id
        WHERE ps.team_id = :team_id AND s.abbreviation = :season
    """
    rows = execute_raw(db, query, {"team_id": team_id, "season": season})
    return rows
