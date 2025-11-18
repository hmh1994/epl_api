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

router = APIRouter(prefix="/api/v1", tags=["league_pulse_05"])

@router.get("/leagues/{leagueId}/meta")
def get_league_meta(
    leagueId: str,
    season: Optional[str] = Query(None),
    locale: Optional[str] = Query("ko-KR"),
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

    ## LeagueMetaMetric
    sql = """
        select 
            id,
            description_en,
            description_kr,
            icon_url
        from competitions
        where id = :competition_id
        LIMIT 1
    """
    params = {"competition_id": competition_id}
    row = db.execute(text(sql), params).fetchone()

    result = None
    if row:
        result = {
            "id": row._mapping["id"],
            "description": row._mapping["description_kr"] if locale == "ko-KR" else row._mapping["description_en"],
            "icon_url": row._mapping["icon_url"]
        }
    
    return {
        "leagueMetaMetric" : result,
        "meta": {
            "season": season_id,
            "leagueId": competition_id,
            "leagueName": leagueId,
            "locale": locale,
        }
    }