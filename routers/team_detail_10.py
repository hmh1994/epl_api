from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from database import get_db

from utils.leagues_util import LEAGUE_ENUM_MAP, get_competition_id


router = APIRouter(prefix="/api/v1", tags=["team_detail_10"])

##TeamProfilesResponse
@router.get("/leagues/{leagueId}/teams/profiles")
def get_team_profiles(
    leagueId: str,
    season: Optional[str] = Query(None),
    locale: Optional[str] = Query("ko-KR"),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    sql = text("SELECT * FROM teams")
    result = db.execute(sql).fetchall()
    return [dict(row._mapping) for row in result]

##TeamSquadResponse
@router.get("/leagues/{leagueId}/teams/{teamId}/squad")
def get_team_squad(
    leagueId: str,
    teamId: str,
    season: Optional[str] = Query(None, description = "If no season is provided, the default value is the latest season"),
    locale: Optional[str] = Query("en-US", description = "support only ko-KR, en-US"),
    db: Session = Depends(get_db),
):
    ## 리그 정보 조회
    competition_id, error = get_competition_id(db, leagueId)
    if error:
        return {"error": error}

    ## 시즌 정보 조회
    if season:  
        # "2024-25" → "24/25"
        season_db = web_to_db_season(season)
        # abbreviation + competition_id → season_id
        season_id = get_season_id_by_abbr(db, competition_id, season_db)
        if not season_id:
            return {"error": f"Season not found: {season}"}
    else:
        # 시즌이 없으면 → 현재 시즌 or 최신 시즌
        season_id = get_current_or_latest_season_id(db, competition_id)
        if not season_id:
            return {"error": "No season data found"}

    
    return {
        "leagueId": leagueId,
        "competitionId": competition_id,
        "teamId": teamId,
        "seasonParam": season,
        "seasonId": season_id,
        "locale": locale,
        "message": "Season resolved successfully. Ready for squad SQL."
    }


'''
    ##TeamProfile

    ##PlayerProfile

    ##ApiResponseMeta

    sql = text("SELECT * FROM teams")
    result = db.execute(sql).fetchall()
    return [dict(row._mapping) for row in result]'''