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

router = APIRouter(prefix="/api/v1", tags=["league_rank_03"])

@router.get("/leagues/{leagueId}/standings")
def get_league_standings(
    leagueId: str,
    season: Optional[str] = Query(None, description="If no season is provided, the default value is the latest season"),
    locale: Optional[str] = Query("en-US", description="support only ko-KR, en-US"),
    includeAdvanced: Optional[bool] = Query(False),
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

    ## 시즌에 해당 하는 팀 정보를 조회
    sql_team_ids = text("""
        SELECT team_id
        FROM team_stats
        WHERE season_id = :season_id
        ORDER BY overall_points DESC, overall_goals_difference DESC
    """)
    #85c2b6fa-88ae-4ba2-b8bd-00b309f4f70c

    team_rows = db.execute(sql_team_ids, {"season_id": season_id}).fetchall()
    team_ids = [row.team_id for row in team_rows]    


    return { 
        "leagueStandingsRow" : team_ids,
        "meta": {
            "leagueId": competition_id,
            "leagueName": leagueId,
            "season": season_id,
        }
    }