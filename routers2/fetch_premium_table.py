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
    season: Optional[str] = Query(None, description="If no season is provided, the default value is the latest season"),
    locale: Optional[str] = Query("en-US", description="support only ko-KR, en-US"),
    venue: Optional[str] = Query("overall", description="overall | home | away"),
    db: Session = Depends(get_db),
):
    ## 1. 리그
    competition_id, error = get_competition_id(db, leagueName)
    if error:
        return {"error": error}

    ## 2. 시즌
    if season:
        season_db = web_to_db_season(season)
        season_id = get_season_id_by_abbr(db, competition_id, season_db)
        if not season_id:
            return {"error": f"Season not found: {season}"}
    else:
        season_id = get_current_or_latest_season_id(db, competition_id)
        if not season_id:
            return {"error": "No season data found"}

    ## 3. 팀 기본 정보
    sql = text("""
        SELECT 
            ts.id AS team_stat_id,
            t.id AS team_id,
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

            ts.home_position,
            ts.home_matches,
            ts.home_matches_won,            
            ts.home_matches_drawn,
            ts.home_matches_lost,
            ts.home_goals_for,
            ts.home_goals_against,
            ts.home_goals_difference,
            ts.home_points,

            ts.away_position,
            ts.away_matches,
            ts.away_matches_won,            
            ts.away_matches_drawn,
            ts.away_matches_lost,
            ts.away_goals_for,
            ts.away_goals_against,
            ts.away_goals_difference,
            ts.away_points,

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
    """)

    rows = db.execute(sql, {"season_id": season_id}).fetchall()

    ## 4. 최근 5경기 form 조회 SQL
    form_sql = text("""
        SELECT
            tsma.is_home,
            m.home_team_score,
            m.away_team_score
        FROM team_stat_match_association tsma
        JOIN matches m ON tsma.match_id = m.id
        WHERE tsma.team_stat_id = :team_stat_id
        ORDER BY tsma.kickoff_time DESC
        LIMIT 5
    """)

    data = []

    for row in rows:
        ## pass accuracy
        if row.overall_stat_attack_passes and row.overall_stat_attack_passes > 0:
            pass_accuracy = round(
                row.overall_stat_attack_passes_successful /
                row.overall_stat_attack_passes,
                2
            )
        else:
            pass_accuracy = None

        ## 최근 5경기 form 계산
        form_rows = db.execute(
            form_sql,
            {"team_stat_id": row.team_stat_id}
        ).fetchall()

        form = []
        for r in form_rows:
            if r.is_home:
                team_score = r.home_team_score
                opp_score = r.away_team_score
            else:
                team_score = r.away_team_score
                opp_score = r.home_team_score

            if team_score > opp_score:
                form.append("W")
            elif team_score == opp_score:
                form.append("D")
            else:
                form.append("L")

        prefix = venue if venue in ["overall", "home", "away"] else "overall"
        data.append({
            "team": {
                "id": row.team_id,
                "name": row.name_en if locale == "en-US" else row.name_kr,
                "shortName": row.short_name_en if locale == "en-US" else row.short_name_kr,
                "logo": row.icon_url,
            },
            "position": getattr(row, f"{prefix}_position"),
            "record" : {
                "played": getattr(row, f"{prefix}_matches"),
                "won": getattr(row, f"{prefix}_matches_won"),
                "drawn": getattr(row, f"{prefix}_matches_drawn"),
                "lost": getattr(row, f"{prefix}_matches_lost"),
                "goalsFor": getattr(row, f"{prefix}_goals_for"),
                "goalsAgainst": getattr(row, f"{prefix}_goals_against"),
                "goalDifference": getattr(row, f"{prefix}_goals_difference"),
                "points": getattr(row, f"{prefix}_points"),
            },
            "form": form,  
            "trend": row.momentum,
            "advancedMetrics": {
                "xG": row.overall_stat_attack_expected_goals,
                "xGA": row.overall_stat_attack_expected_assists,
                "possession": row.overall_stat_average_possession,
                "passAccuracy": pass_accuracy,
                "cleanSheets": row.overall_stat_defense_clean_sheets,
            }
        })

    ## 5. lastUpdated (KST)
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
