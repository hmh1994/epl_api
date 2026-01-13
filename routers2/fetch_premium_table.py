from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from database import get_db
from datetime import datetime, timedelta, timezone

from utils.leagues_util import LEAGUE_ENUM_MAP, get_competition_id
from utils.seasons_util import (
    web_to_db_season,
    get_season_id_by_abbr,
    get_current_or_latest_season_id
)

router = APIRouter(prefix="/api/v1", tags=["fetch_premium_table"])
@router.get("/leagues/{leagueName}/teams")
def fetch_premium_table(
    leagueName: str,
    season: Optional[str] = Query(
        None, description="If no season is provided, the default value is the latest season"
    ),
    locale: Optional[str] = Query("en-US", description="support only ko-KR, en-US"),
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

    ## 팀 정보 조회
    sql = """
        SELECT 
            t.id,
            t.name_en,
            t.name_kr,
            t.short_name_en,
            t.short_name_kr,
            t.icon_url,

            ts.overall_position,
            ts.overall_matches,
            ts.overall_matches_won,
            ts.overall_matches_drawn,
            ts.overall_matches_lost,
            ts.overall_goals_for,
            ts.overall_goals_against,
            ts.overall_goals_difference,
            ts.overall_points,
            ts.momentum,
            ts.overall_stat_attack_expected_goals,
            ts.overall_stat_attack_expected_assists,
            ts.overall_stat_average_possession,
            ts.overall_stat_attack_passes_successful,
            ts.overall_stat_attack_passes,
            ts.overall_stat_defense_clean_sheets
        FROM team_stats ts
        JOIN teams t ON ts.team_id = t.id
        WHERE ts.season_id = :season_id
        ORDER BY ts.overall_position
    """

    rows = db.execute(text(sql), {"season_id": season_id}).fetchall()

    data = []
    for row in rows:
        # pass accuracy 계산
        if row.overall_stat_attack_passes and row.overall_stat_attack_passes > 0:
            pass_accuracy = round(
                row.overall_stat_attack_passes_successful / row.overall_stat_attack_passes,
                2
            )
        else:
            pass_accuracy = None

        data.append({
            "team": {
                "id": row.id,
                "name": row.name_en if locale == "en-US" else row.name_kr,
                "shortName": row.short_name_en if locale == "en-US" else row.short_name_kr,
                "logo": row.icon_url,
            },
            "position": row.overall_position,
            "record": {
                "played": row.overall_matches,
                "won": row.overall_matches_won,
                "drawn": row.overall_matches_drawn,
                "lost": row.overall_matches_lost,
                "goalsFor": row.overall_goals_for,
                "goalsAgainst": row.overall_goals_against,
                "goalDifference": row.overall_goals_difference,
                "points": row.overall_points,
            },
            "form": None,
            "trend": row.momentum,
            "advancedMetrics": {
                "xG": row.overall_stat_attack_expected_goals,
                "xGA": row.overall_stat_attack_expected_assists,
                "possession": row.overall_stat_average_possession,
                "passAccuracy": pass_accuracy,
                "cleanSheets": row.overall_stat_defense_clean_sheets,
                "bigChances": None,
            }
        })

    KST = timezone(timedelta(hours=9))
    last_updated = datetime.now(KST).strftime("%Y-%m-%dT%H:%M:%S")

    return {
        "data": data,
        "meta": {
            "leagueName": leagueName,
            "leagueId": competition_id,
            "season": season_id,
            "lastUpdated": last_updated,
            "locale": locale,
        }
    }

    '''
@router.get("/leagues/{leagueName}/teams")
def fetch_premium_table(
    leagueName: str,
    season: Optional[str] = Query(None, description="If no season is provided, the default value is the latest season"),
    locale: Optional[str] = Query("en-US", description="support only ko-KR, en-US"),
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

     # 팀 정보 조회
    sql = """
        SELECT 
            t.id,
            t.name_en,
            t.name_kr,
            t.short_name_en,
            t.short_name_kr,
            t.icon_url,

            ts.overall_position,
            ts.overall_matches,
            ts.overall_matches_won,
            ts.overall_matches_drawn,
            ts.overall_matches_lost,
            ts.overall_goals_for,
            ts.overall_goals_against,
            ts.overall_goals_difference,
            ts.overall_points,

            ts.overall_stat_attack_expected_goals,
            ts.overall_stat_attack_expected_assists,
            ts.overall_stat_average_possession,
            ts.overall_stat_attack_passes_successful,
            ts.overall_stat_attack_passes,
            ts.overall_stat_defense_clean_sheets
        FROM team_stats ts
        JOIN teams t ON ts.team_id = t.id
        WHERE ts.season_id = :season_id
    """
    params = {"season_id": season_id}
    rows = db.execute(text(sql), params).fetchall()

    field = []
    for row in rows:
        if row.overall_stat_attack_passes and row.overall_stat_attack_passes > 0:
            pass_accuracy = round(
                row.overall_stat_attack_passes_successful / row.overall_stat_attack_passes,
                2
            )
        else:
            pass_accuracy = 0.0
        field.append({
            "id" : row.id,
            "name" : row.name_en if locale == "en-US" else row.name_kr,
            "shortName" : row.short_name_en if locale == "en-US" else row.short_name_kr,
            "logo" : row.icon_url,
            "position" : row.overall_position,
            "played" : row.overall_matches,
            "won" : row.overall_matches_won,
            "drawn" : row.overall_matches_drawn,
            "lost" : row.overall_matches_lost,
            "goalsFor" : row.overall_goals_for,
            "goalsAgainst" : row.overall_goals_against,
            "goalDifference" : row.overall_goals_difference,
            "points" : row.overall_points,
            "form" : None,
            "trend" : None,
            "xG" : row.overall_stat_attack_expected_goals,
            "xGA" : row.overall_stat_attack_expected_assists,
            "possession" : row.overall_stat_average_possession,
            "passAccuracy" : pass_accuracy,
            "cleanSheets" : row.overall_stat_defense_clean_sheets 
        })


    KST = timezone(timedelta(hours=9))
    #last_updated = datetime.now(KST).isoformat()
    last_updated = datetime.now(KST).strftime("%Y-%m-%dT%H:%M:%S")

    return {
        "data" : field,
        "meta": {
            "leagueName": leagueName,
            "leagueId": competition_id,
            "season": season_id,
            "lastUpdated" : last_updated,
            "locale": locale,
        }
    }
    '''