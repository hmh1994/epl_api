from collections import defaultdict
from datetime import datetime, timedelta, timezone
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

router = APIRouter(prefix="/api/v1", tags=["fetch_match_detail"])

@router.get("/leagues/{leagueName}/matches/{matchId}")
def fetch_match_detail(
    leagueName: str,
    matchId: str,
    season: Optional[str] = Query(None),
    locale: Optional[str] = Query("en-US"),
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
        SELECT id from fixtures where id = :match_id 
    """
    params = {
        "match_id": matchId
    }
    row = db.execute(text(sql), params).fetchone()

    return {
        "data": dict(row._mapping)  # ✅ 핵심 수정
    }
