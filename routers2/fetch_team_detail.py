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
router = APIRouter(prefix="/api/v1", tags=["fetch_team_detail"])
@router.get("/leagues/{leagueName}/teams/{teamId}")
def fetch_team_detail(
    leagueName: str,
    teamId: str,
    season: Optional[str] = Query(None, description = "If no season is provided, the default value is the latest season"),
    locale: Optional[str] = Query("en-US", description = "support only ko-KR, en-US"),
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
    
    ## TeamProfile
    ### 1
    sql_team = text("""
        SELECT id, name_en, name_kr, short_name_en, short_name_kr, icon_url, founded_year
        FROM teams
        WHERE id = :team_id
    """)
    team_row = db.execute(sql_team, {"team_id": teamId}).fetchone()
    if not team_row:
        return {"error": "Team not found"}

    team_profile = dict(team_row._mapping)
    
    ### 2
    sql_ground = text("""
        SELECT g.name_en as ground_name_en, g.name_kr as ground_name_kr, g.capacity
        FROM grounds g
        JOIN team_stats ts ON g.id = ts.ground_id
        WHERE ts.season_id = :season_id AND ts.team_id = :team_id
        LIMIT 1
    """)
    ground_row = db.execute(sql_ground, {"season_id": season_id, "team_id": teamId}).fetchone()
    team_profile["ground_name_en"] = ground_row._mapping["ground_name_en"] if ground_row else None
    team_profile["ground_name_kr"] = ground_row._mapping["ground_name_kr"] if ground_row else None
    team_profile["ground_capacity"] = ground_row._mapping["capacity"] if ground_row else None

    ### 3
    sql_rank = text("""
        SELECT rank
        FROM (
            SELECT 
                team_id,
                ROW_NUMBER() OVER (
                    ORDER BY overall_points DESC, overall_goals_difference DESC
                ) AS rank
            FROM team_stats
            WHERE season_id = :season_id
        ) ranked
        WHERE team_id = :team_id
        LIMIT 1
    """)
    rank_row = db.execute(sql_rank, {"season_id": season_id, "team_id": teamId}).fetchone()
    team_profile["rank"] = rank_row._mapping["rank"] if rank_row else None

    ### 4
    sql_stats = text("""
        SELECT 
            (SELECT display_name_en FROM staffs WHERE id = ts.manager_id) AS manager_en,
            (SELECT display_name_kr FROM staffs WHERE id = ts.manager_id) AS manager_kr,
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
    
    team_profile_localized = {
        "id": team_profile["id"],
        "name": team_profile["name_en"] if locale == "en-US" else team_profile["name_kr"],
        "shortName": team_profile["short_name_en"] if locale == "en-US" else team_profile["short_name_kr"],
        "logo": team_profile["icon_url"],
        "founded": team_profile["founded_year"],
        "stadium": team_profile["ground_name_en"] if locale == "en-US" else team_profile["ground_name_kr"],
        "capacity": team_profile["ground_capacity"],
        "rank": team_profile["rank"],
        "manager": team_profile["manager_en"] if locale == "en-US" else team_profile["manager_kr"],
        "points": team_profile.get("overall_points"),
        "played": team_profile.get("overall_matches"),
        "won": team_profile.get("overall_matches_won"),
        "drawn": team_profile.get("overall_matches_drawn"),
        "lost": team_profile.get("overall_matches_lost"),
        "goalsFor": team_profile.get("overall_goals_for"),
        "goalsAgainst": team_profile.get("overall_goals_against"),
    }
    ## teamSquad
    sql_squad = text("""
        SELECT 
            p.id AS player_id,
            ps.number,
            p.display_name_en,
            p.display_name_kr,
            p.position,
            EXTRACT(YEAR FROM AGE(CURRENT_DATE, p.birth_date)) AS age,
            p.nationality_en,
            p.nationality_kr,
            COALESCE(ps.shooting_goals, 0) AS shooting_goals,
            COALESCE(ps.passing_assists, 0) AS passing_assists,
            COALESCE(ps.appearances, 0) AS appearances
        FROM players p
        JOIN player_stats ps
            ON p.id = ps.player_id
        WHERE ps.team_id = :team_id
        AND ps.season_id = :season_id
    """)
    squad_rows = db.execute(sql_squad, {"team_id": teamId, "season_id": season_id}).fetchall()
    squad = []
    for row in squad_rows:
        squad.append({
            "id":row.player_id,
            "number":row.number,
            "name":row.display_name_en if locale == "en-US" else row.display_name_kr,
            "position":row.position,
            "age":row.age,
            "nationality":row.nationality_en if locale == "en-US" else row.nationality_kr,
            "teamId":teamId,
            "rating":None,
            "goals":row.shooting_goals,
            "assists":row.passing_assists,
            "appearances":row.appearances,
        })

    KST = timezone(timedelta(hours=9))
    #last_updated = datetime.now(KST).isoformat()
    last_updated = datetime.now(KST).strftime("%Y-%m-%dT%H:%M:%S")
    return {
        "data": {
        **team_profile_localized,
        "squad": squad
        },
        "meta": {
            "season": season_id,
            "leagueId": competition_id,
            "leagueName": leagueName,
            "teamId": teamId,
            "lastUpdated" : last_updated,
            "locale" : locale
        }
    }

