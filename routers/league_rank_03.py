from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from database import get_db

from utils.leagues_util import LEAGUE_ENUM_MAP, get_competition_id
from utils.seasons_util import (
    web_to_db_season,
    get_season_id_by_abbr,
    get_current_or_latest_season_id
)

router = APIRouter(prefix="/api/v1", tags=["league_rank_03"])

@router.get("/leagues/{leagueId}/standings")
def get_league_standings(
    leagueId: str,
    season: Optional[str] = Query(None, description="If no season is provided, the default value is the latest season"),
    locale: Optional[str] = Query("en-US", description="support only ko-KR, en-US"),
    includeAdvanced: Optional[bool] = Query(False),
    db: Session = Depends(get_db),
):
    ## 리그 정보 조회
    competition_id, error = get_competition_id(db, leagueId)
    if error:
        return {"error": error}

    ## 시즌 정보 조회
    if season:  
        season_db = web_to_db_season(season)
        season_id = get_season_id_by_abbr(db, competition_id, season_db)
        if not season_id:
            return {"error": f"Season not found: {season}"}
    else:
        season_id = get_current_or_latest_season_id(db, competition_id)
        if not season_id:
            return {"error": "No season data found"}

    ## 시즌에 해당 하는 팀 정보를 조회
    sql_team_ids = text("""
        SELECT team_id
        FROM team_stats
        WHERE season_id = :season_id
        ORDER BY overall_points DESC, overall_goals_difference DESC
    """)
    #85c2b6fa-88ae-4ba2-b8bd-00b309f4f70c

    team_rows = db.execute(sql_team_ids, {"season_id": season_id}).fetchall()
    team_ids = [row.team_id for row in team_rows]    
    
    result = []
    for rank, team_id in enumerate(team_ids, start=1):
        # 기본 팀 + 기록 정보 조회
        sql = text("""
            SELECT 
                t.id,
                t.name_en,
                t.name_kr,
                t.short_name_en,
                t.short_name_kr,
                g.name_en AS stadium_en,
                g.name_kr AS stadium_kr,
                g.city_name_en AS city_en,
                g.city_name_kr AS city_kr,
                ts.overall_matches,
                ts.overall_matches_won,
                ts.overall_matches_drawn,
                ts.overall_matches_lost,
                ts.overall_goals_for,
                ts.overall_goals_against,
                ts.overall_goals_difference,
                ts.overall_points,
                ts.overall_stat_average_possession
            FROM team_stats ts
            JOIN teams t ON ts.team_id = t.id
            LEFT JOIN grounds g ON ts.ground_id = g.id
            WHERE ts.team_id = :team_id AND ts.season_id = :season_id
            LIMIT 1
        """)
        row = db.execute(sql, {"team_id": team_id, "season_id": season_id}).fetchone()
        if not row:
            continue

        team_summary = {
            "id": row._mapping["id"],
            "name": row._mapping["name_en"] if locale == "en-US" else row._mapping["name_kr"],
            "shortName": row._mapping["short_name_en"] if locale == "en-US" else row._mapping["short_name_kr"],
            "city": row._mapping["city_en"] if locale == "en-US" else row._mapping["city_kr"],
            "stadium": row._mapping["stadium_en"] if locale == "en-US" else row._mapping["stadium_kr"],
        }

        record = {
            "rank": rank,
            "played": row._mapping["overall_matches"],
            "won": row._mapping["overall_matches_won"],
            "drawn": row._mapping["overall_matches_drawn"],
            "lost": row._mapping["overall_matches_lost"],
            "goalsFor": row._mapping["overall_goals_for"],
            "goalsAgainst": row._mapping["overall_goals_against"],
            "goalDifference": row._mapping["overall_goals_difference"],
            "points": row._mapping["overall_points"]
        }

        team_entry = {"teamSummary": team_summary, "record": record}

        if includeAdvanced:
            team_entry["advancedMetrics"] = {
                "possession": row._mapping["overall_stat_average_possession"],
            }

        result.append(team_entry)

    return {
        "leagueStandingsRow": result,
        "meta": {
            "leagueId": competition_id,
            "leagueName": leagueId,
            "season": season_id,
        }
    }