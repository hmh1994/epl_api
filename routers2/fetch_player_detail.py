from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from datetime import datetime, timedelta, timezone
from database import get_db

from utils.leagues_util import LEAGUE_ENUM_MAP, get_competition_id
from utils.seasons_util import (
    web_to_db_season,
    get_season_id_by_abbr,
    get_current_or_latest_season_id
)

router = APIRouter(prefix="/api/v1", tags=["fetch_player_detail"])

@router.get("/leagues/{leagueName}/player/{playerId}")
def fetch_player_detail(
    leagueName: str,
    playerId: str,
    season: Optional[str] = Query(None, description="If no season is provided, the default value is the latest season"),
    locale: Optional[str] = Query("en-US", description="support only ko-KR, en-US"),
    db: Session = Depends(get_db),
): 
    ## 리그 정보 조회
    competition_id, error = get_competition_id(db, leagueName)
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

    sql = """
        SELECT 
            p.id,
            p.display_name_en,
            p.display_name_kr,
            ps.team_id,
            ts.name_en AS team_name_en,
            ts.name_kr AS team_name_kr,
            p.position,
            p.photo_url,
            p.nationality_en,
            p.nationality_kr,
            DATE_PART('year', AGE(CURRENT_DATE, p.birth_date)) AS age,
            p.height,
            p.weight,
            ps.shooting_goals,
            ps.passing_assists,
            ps.appearances,

            ps.score_overall,
            ps.score_shooting,
            ps.score_passing,
            ps.score_dribbling,
            ps.score_defending,
            ps.score_discipline
        FROM players p
        JOIN player_stats ps ON p.id = ps.player_id
        JOIN teams ts ON ps.team_id = ts.id
        WHERE ps.season_id = :season_id
        AND p.id = :player_id
    """
    params = {
        "season_id": season_id,
        "player_id": playerId,
    }
    row = db.execute(text(sql), params).fetchone()

    name = row.display_name_en if locale == "en-US" else row.display_name_kr
    nationality = row.nationality_en if locale == "en-US" else row.nationality_kr

    career_sql = """
            SELECT
                s.id AS season_id,
                ps.team_id,
                ps.appearances,
                ps.shooting_goals
            FROM player_stats ps
            JOIN seasons s ON ps.season_id = s.id
            WHERE ps.player_id = :player_id
            ORDER BY s.id DESC
        """
    career_rows = db.execute(
        text(career_sql),
        {"player_id": playerId}
    ).fetchall()

    career = []
    for r in career_rows:
        career.append({
            "year": r.season_id,
            "teamId": r.team_id,
            "matches": r.appearances or 0,
            "goals": r.shooting_goals or 0
        })
    

    data = {
        "summary": {
            "id": row.id,
            "name": name,
            "teamId": row.team_id,
            "teamName" : row.team_name_en if locale == "en-US" else row.team_name_kr,
            "position": row.position,
            "photo": row.photo_url,
            "nationality": nationality,
            "age": row.age,
            "height": row.height,
            "weight": row.weight,
        },
        "attributes": {
            "pace": row.score_overall,
            "shooting": row.score_shooting,
            "passing": row.score_passing,
            "dribbling": row.score_dribbling,
            "defending": row.score_defending,
            "physical": row.score_discipline,
        },
        "performance": {
            "goals": row.shooting_goals,
            "assists": row.passing_assists,
            "pace": row.score_overall,
            "matches": row.appearances,
        },
        "career": career
    }

    KST = timezone(timedelta(hours=9))
    last_updated = datetime.now(KST).strftime("%Y-%m-%dT%H:%M:%S")
    return {
        "data" : data,
        "meta" : {
            "leagueName": leagueName,
            "leagueId": competition_id,
            "playerId" : playerId,
            "season" : season_id,
            "locale" : locale,
            "lastUpdated" : last_updated,
        }
    }