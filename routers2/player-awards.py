from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from database import get_db
from datetime import datetime, timedelta, timezone

from utils.leagues_util import get_competition_id

router = APIRouter(prefix="/api/v1", tags=["player-award"])


@router.get("/leagues/{leagueName}/players/{playerId}/awards")
def player_award(
    leagueName: str,
    playerId: str,
    season: Optional[str] = Query(None, description="If no season is provided, the default value is the latest season"),
    locale: Optional[str] = Query("en-US", description="support only ko-KR, en-US"),
    db: Session = Depends(get_db),
):

    # -----------------------------
    # 1️⃣ league 확인
    # -----------------------------
    competition_id, error = get_competition_id(db, leagueName)
    if error:
        return {"error": error}

    # -----------------------------
    # 2️⃣ award 조회
    # -----------------------------
    sql = text("""
        SELECT
            a.type,
            a.name_en,
            a.name_kr,
            a.description_en,
            a.description_kr,
            a.icon_url,
            psaa.date,
            s.abbreviation AS season
        FROM player_stats ps
        JOIN player_stat_award_association psaa
            ON ps.id = psaa.player_stat_id
        JOIN awards a
            ON psaa.award_id = a.id
        JOIN seasons s
            ON ps.season_id = s.id
        WHERE ps.player_id = :player_id
        ORDER BY psaa.date DESC
    """)

    rows = db.execute(sql, {"player_id": playerId}).fetchall()

    data = []

    for row in rows:
        data.append({
            "type": row.type,
            "name": row.name_en if locale == "en-US" else row.name_kr,
            "description": row.description_en if locale == "en-US" else row.description_kr,
            "iconUrl": row.icon_url,
            "date": row.date,
            "season": row.season
        })

    # -----------------------------
    # 3️⃣ 메타 정보
    # -----------------------------
    total_count = len(data)

    if total_count == 0:
        data = []
        message = "No awards found for this player"
    else:
        message = None

    return {
        "data": data,
        "meta": {
            "totalCount": total_count,
            "leagueId": competition_id,
            "locale": locale,
            "message": message
        }
    }