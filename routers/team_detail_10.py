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

    ## TeamProfile
    sql_team = text("""
        SELECT id, name_en, short_name_en, icon_url, founded_year
        FROM teams
        WHERE id = :team_id
    """)
    team_row = db.execute(sql_team, {"team_id": teamId}).fetchone()
    if not team_row:
        return {"error": "Team not found"}

    team_profile = dict(team_row._mapping)

    sql_ground = text("""
        SELECT g.name_en AS ground_name, g.capacity
        FROM grounds g
        JOIN team_stats ts ON g.id = ts.ground_id
        WHERE ts.season_id = :season_id AND ts.team_id = :team_id
        LIMIT 1
    """)
    ground_row = db.execute(sql_ground, {"season_id": season_id, "team_id": teamId}).fetchone()
    team_profile["ground_name"] = ground_row._mapping["ground_name"] if ground_row else None
    team_profile["ground_capacity"] = ground_row._mapping["capacity"] if ground_row else None

    sql_stats = text("""
        SELECT 
            (SELECT display_name_en FROM staffs WHERE id = ts.manager_id) AS manager,
            ts.overall_points,
            ts.overall_matches,
            ts.overall_matches_won,
            ts.overall_matches_drawn,
            ts.overall_matches_lost,
            ts.overall_goals_for,
            ts.overall_goals_against
        FROM team_stats ts
        WHERE ts.season_id = :season_id AND ts.team_id = :team_id
        LIMIT 1
    """)
    stats_row = db.execute(sql_stats, {"season_id": season_id, "team_id": teamId}).fetchone()
    if stats_row:
        team_profile.update(dict(stats_row._mapping))
    else:
        team_profile.update({
            "manager": None,
            "overall_points": None,
            "overall_matches": None,
            "overall_matches_won": None,
            "overall_matches_drawn": None,
            "overall_matches_lost": None,
            "overall_goals_for": None,
            "overall_goals_against": None,
        })

    return {
        "data": {
            "team": team_profile
        },
        "meta": {
            "teamId": teamId,
            "season": season_id
        }
    }