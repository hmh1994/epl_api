from database import execute_raw

async def get_league_standings(db, league_id: str, season: str, include_advanced: bool = False):
    query = """
        SELECT t.id AS team_id, t.name_en AS name, ts.overall_position::int AS pos,
               ts.overall_matches::int AS played, ts.overall_matches_won::int AS won,
               ts.overall_matches_drawn::int AS drawn, ts.overall_matches_lost::int AS lost,
               ts.overall_goals_for::int AS goals_for, ts.overall_goals_against::int AS goals_against,
               ts.overall_goals_difference::int AS gd, ts.overall_points::int AS pts,
               ts.overall_stat_average_possession::float AS possession,
               ts.overall_stat_attack_expected_goals::float AS xG,
               ts.overall_stat_defense_duels_won::float AS duels_won
        FROM teams t
        LEFT JOIN team_stats ts ON t.id = ts.team_id
        LEFT JOIN seasons s ON ts.season_id = s.id
        LEFT JOIN competitions c ON s.competition_id = c.id
        WHERE c.abbreviation = :league_id AND s.abbreviation = :season
        ORDER BY ts.overall_position::int ASC
    """
    rows = execute_raw(db, query, {"league_id": league_id, "season": season})
    return rows

async def get_league_metadata(db, league_id: str, season: str):
    # 예: 챔피언, 주요 지표 등
    standings = await get_league_standings(db, league_id, season)
    champions = [s for s in standings if s["pos"] == 1]
    return {"standings": standings, "champions": champions}
