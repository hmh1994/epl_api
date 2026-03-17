from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from database import get_db

from utils.leagues_util import get_competition_id
from utils.seasons_util import (
    web_to_db_season,
    get_season_id_by_abbr
)

router = APIRouter(prefix="/api/v1", tags=["player-award"])


@router.get("/leagues/{leagueName}/players/{playerId}/awards")
def player_award(
    leagueName: str,
    playerId: str,
    season: Optional[str] = Query(None, description="optional season filter"),
    locale: Optional[str] = Query("en-US", description="support only ko-KR, en-US"),
    db: Session = Depends(get_db),
):

    # 1️⃣ league 확인
    competition_id, error = get_competition_id(db, leagueName)
    if error:
        return {"error": error}

    season_id = None

    # 2️⃣ season 파라미터 있을 때만 조회
    if season:
        season_db = web_to_db_season(season)
        season_id = get_season_id_by_abbr(db, competition_id, season_db)
        if not season_id:
            return {"error": f"Season not found: {season}"}

    # 3️⃣ SQL (season 조건 동적 추가)
    sql = """
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
    """

    params = {"player_id": playerId}

    if season_id:
        sql += " AND ps.season_id = :season_id"
        params["season_id"] = season_id

    sql += " ORDER BY psaa.date DESC"

    rows = db.execute(text(sql), params).fetchall()

    # 4️⃣ 데이터 변환
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

    total_count = len(data)

    if total_count == 0:
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