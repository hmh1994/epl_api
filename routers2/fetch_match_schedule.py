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

router = APIRouter(prefix="/api/v1", tags=["fetch_match_schedule"])
@router.get("/leagues/{leagueName}/matches")
def fetch_match_schedule(
    leagueName: str,
    season: Optional[str] = Query(None, description="If no season is provided, the default value is the latest season"),
    locale: Optional[str] = Query("en-US", description="support only ko-KR, en-US"),
    matchweek: Optional[int] = Query(1, ge=1),
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
        select 
            fx.kickoff_time,
            fx.id,
            fx.game_week,
            fx.ground_id 
        from fixtures fx
        where fx.season_id = :season_id and fx.game_week = :matchweek
    """)
    rows = db.execute(sql, {"season_id": season_id, "matchweek": matchweek}).fetchall()

    match_list = []
    for row in rows:
        match_list.append({
            "date": row.kickoff_time,
            "id": row.id,
            "matchweek" : row.game_week,
            "kickoff" : row.kickoff_time
        })

    KST = timezone(timedelta(hours=9))
    last_updated = datetime.now(KST).strftime("%Y-%m-%dT%H:%M:%S")

    return {
        "data": match_list,
        "meta": {
            "leagueName": leagueName,
            "leagueId": competition_id,
            "season": season_id,
            "lastUpdated": last_updated,
            "locale": locale,
        }
    }