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

router = APIRouter(prefix="/api/v1", tags=["team_info_01"])

@router.get("/teams")
def get_teams(
    season: Optional[str] = Query(None, description = "If no season is provided, the default value is the latest season"),
    locale: Optional[str] = Query("en-US", description = "support only ko-KR, en-US"),
    leagueId: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    # 리그 정보 조회 (optional)
    competition_id = None
    if leagueId:
        competition_id, error = get_competition_id(db, leagueId)
        if error:
            return {"error": error}

    # 시즌 정보 조회
    if season:
        season_db = web_to_db_season(season)
        season_id = get_season_id_by_abbr(db, competition_id, season_db)
        if not season_id:
            return {"error": f"Season not found: {season}"}
    else:
        season_id = get_current_or_latest_season_id(db, competition_id)
        if not season_id:
            return {"error": "No season data found"}

    # 팀 정보 조회
    sql = """
        SELECT 
            t.id,
            t.name_en,
            t.name_kr,
            t.short_name_en,
            t.short_name_kr,
            g.name_en AS stadium_en,
            g.name_kr AS stadium_kr,
            g.city_name_en AS city_en,
            g.city_name_kr AS city_kr
        FROM team_stats ts
        JOIN teams t ON ts.team_id = t.id
        LEFT JOIN grounds g ON ts.ground_id = g.id
        WHERE ts.season_id = :season_id
    """

    params = {"season_id": season_id}

    if competition_id:
        sql += " AND ts.competition_id = :competition_id"
        params["competition_id"] = competition_id

    if search:
        sql += " AND (t.name_en ILIKE :search OR t.name_kr ILIKE :search OR t.short_name_en ILIKE :search OR t.short_name_kr ILIKE :search OR g.city_name_en ILIKE :search OR g.city_name_kr ILIKE :search)"
        params["search"] = f"%{search}%"

    sql += " ORDER BY t.name_en"

    rows = db.execute(text(sql), params).fetchall()

    teams = []
    for row in rows:
        teams.append({
            "id": row._mapping["id"],
            "name": {"en": row._mapping["name_en"], "kr": row._mapping["name_kr"]},
            "shortName": {"en": row._mapping["short_name_en"], "kr": row._mapping["short_name_kr"]},
            "city": {"en": row._mapping["city_en"], "kr": row._mapping["city_kr"]} if row._mapping["city_en"] or row._mapping["city_kr"] else None,
            "stadium": {"en": row._mapping["stadium_en"], "kr": row._mapping["stadium_kr"]} if row._mapping["stadium_en"] or row._mapping["stadium_kr"] else None
        })

    return {
        "teams": teams,
        "meta": {
            "season": season_id,
            "leagueId": competition_id,
            "leagueName": leagueId,
            "locale": locale,
            "total": len(teams),
        }
    }