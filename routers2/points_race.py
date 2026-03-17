from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from database import get_db
from datetime import datetime, timedelta, timezone

from utils.leagues_util import LEAGUE_ENUM_MAP, get_competition_id
from utils.seasons_util import (
    web_to_db_season,
    get_season_id_by_abbr,
    get_current_or_latest_season_id
)

router = APIRouter(prefix="/api/v1", tags=["points-race"])
@router.get("/leagues/{leagueName}/teams/points-race")
def points_race(
    leagueName: str,
    season: Optional[str] = Query(None, description="If no season is provided, the default value is the latest season"),
    locale: Optional[str] = Query("en-US", description="support only ko-KR, en-US"),
    db: Session = Depends(get_db),
):
    ## 1. 리그
    competition_id, error = get_competition_id(db, leagueName)
    if error:
        return {"error": error}

    ## 2. 시즌
    if season:
        season_db = web_to_db_season(season)
        season_id = get_season_id_by_abbr(db, competition_id, season_db)
        if not season_id:
            return {"error": f"Season not found: {season}"}
    else:
        season_id = get_current_or_latest_season_id(db, competition_id)
        if not season_id:
            return {"error": "No season data found"}

    sql = text("""
        SELECT 
            ts.id AS team_stat_id,
            t.id AS team_id,
            t.name_en,
            t.name_kr,
            t.short_name_en,
            t.short_name_kr,
            t.icon_url,
            ts.overall_position,
            ts.overall_cumulative_points
        FROM team_stats ts
        JOIN teams t ON ts.team_id = t.id
        WHERE ts.season_id = :season_id
        ORDER BY ts.overall_position
    """)

    rows = db.execute(sql, {"season_id": season_id}).fetchall()
    data = []
    for row in rows:
        data.append({
            
                "id": row.team_id,
                "name": row.name_en if locale == "en-US" else row.name_kr,
                "shortName": row.short_name_en if locale == "en-US" else row.short_name_kr,
                "logo": row.icon_url,
                "position" : row.overall_position,
                "cumulativePoints" : row.overall_cumulative_points
            
        })


    KST = timezone(timedelta(hours=9))
    last_updated = datetime.now(KST).strftime("%Y-%m-%dT%H:%M:%S")

    return {
        "data": data,
        "meta": {
            "leagueName": leagueName,
            "leagueId": competition_id,
            "season": season_id,
            "lastUpdated": last_updated,
            "locale": locale
        }
    }