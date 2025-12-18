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
router = APIRouter(prefix="/api/v1", tags=["fetch_season_analytics"])

@router.get("/leagues/{leagueName}/season/stat")
def fetch_season_analytics(
    leagueName: str,
    season: Optional[str] = Query(None),
    locale: Optional[str] = Query("en-US"),
    db: Session = Depends(get_db),
):
    # 1. 리그
    competition_id, error = get_competition_id(db, leagueName)
    if error:
        return {"error": error}

    # 2. 시즌
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
            a.id,
            a.key AS analytics_key,
            a.title_en,
            a.title_kr,
            a.value,
            a.delta,
            a.description_en,
            a.description_kr
        FROM analytics a
        WHERE a.season_id = :season_id
        ORDER BY a.id ASC
    """)

    rows = db.execute(
        sql,
        {
            "competition_id": competition_id,
            "season_id": season_id
        }
    ).fetchall()

    # 4. metrics 구성
    metrics = []
    for row in rows:
        metrics.append({
            "id": row.id,
            "key": row.analytics_key,
            "title": row.title_en if locale == "en-US" else row.title_kr,
            "value": row.value,
            "delta": row.delta,
            "description": row.description_en if locale == "en-US" else row.description_kr
        })

    # 5. lastUpdated (KST, +09:00 제거 포맷)
    KST = timezone(timedelta(hours=9))
    last_updated = datetime.now(KST).strftime("%Y-%m-%dT%H:%M:%S")

    # 6. 최종 응답
    return {
        "metrics": metrics,
        "meta": {
            "leagueName": leagueName,
            "leagueId": competition_id,
            "season": season_id,
            "lastUpdated": last_updated,
            "locale": locale
        }
    }