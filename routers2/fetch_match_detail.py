from collections import defaultdict
from datetime import datetime, timedelta, timezone
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

router = APIRouter(prefix="/api/v1", tags=["fetch_match_detail"])

@router.get("/leagues/{leagueName}/matches/{matchId}")
def fetch_match_detail(
    leagueName: str,
    matchId: str,
    season: Optional[str] = Query(None),
    locale: Optional[str] = Query("en-US"),
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

    sql = """
        SELECT 
            fx.kickoff_time,
            fx.id,
            fx.game_week,
            gr.name_en,
            gr.name_kr,
            gr.city_name_en,
            gr.city_name_kr,
            ma.period,

            ma.home_team_id,
            ht.name_en AS home_team_name_en,
            ht.name_kr AS home_team_name_kr,
            ma.home_team_score,
            hts.id AS home_team_stat_id,
            hts.overall_position AS home_position,

            ma.away_team_id,
            at.name_en AS away_team_name_en,
            at.name_kr AS away_team_name_kr,
            ma.away_team_score,
            ats.id AS away_team_stat_id,
            ats.overall_position AS away_position,

            main_ref.display_name_en   AS referee_main_en,
            main_ref.display_name_kr   AS referee_main_kr,
            a1_ref.display_name_en     AS referee_a1_en,
            a1_ref.display_name_kr     AS referee_a1_kr,
            a2_ref.display_name_en     AS referee_a2_en,
            a2_ref.display_name_kr     AS referee_a2_kr,
            fourth_ref.display_name_en AS referee_4th_en,
            fourth_ref.display_name_kr AS referee_4th_kr,

            ma.attendance      
        FROM fixtures fx
        JOIN grounds gr ON fx.ground_id = gr.id
        JOIN matches ma ON fx.id = ma.fixture_id
        LEFT JOIN officials main_ref ON ma.official_main_referee_id = main_ref.id
        LEFT JOIN officials a1_ref ON ma.official_assistant_1_referee_id = a1_ref.id
        LEFT JOIN officials a2_ref ON ma.official_assistant_2_referee_id = a2_ref.id
        LEFT JOIN officials fourth_ref ON ma.official_fourth_referee_id = fourth_ref.id
        LEFT JOIN team_stats hts ON ma.home_team_id = hts.team_id AND hts.season_id = :season_id
        LEFT JOIN team_stats ats ON ma.away_team_id = ats.team_id AND ats.season_id = :season_id
        LEFT JOIN teams ht ON ma.home_team_id = ht.id
        LEFT JOIN teams at ON ma.away_team_id = at.id
        WHERE fx.id = :match_id
    """
    params = {
        "season_id": season_id,
        "match_id": matchId
    }
    row = db.execute(text(sql), params).fetchone()
    
    form_sql = text("""
        SELECT
            tsma.is_home,
            m.home_team_score,
            m.away_team_score
        FROM team_stat_match_association tsma
        JOIN matches m ON tsma.match_id = m.id
        WHERE tsma.team_stat_id = :team_stat_id
          AND tsma.kickoff_time < :fixture_kickoff
        ORDER BY tsma.kickoff_time DESC
        LIMIT 5
    """)

    def get_recent_form(team_stat_id: str, fixture_kickoff: datetime):
        if not team_stat_id:
            return []

        rows = db.execute(form_sql, {
            "team_stat_id": team_stat_id,
            "fixture_kickoff": fixture_kickoff,
        }).fetchall()

        form = []
        for r in rows:
            if r.is_home:
                team_score, opp_score = r.home_team_score, r.away_team_score
            else:
                team_score, opp_score = r.away_team_score, r.home_team_score

            if team_score > opp_score:
                form.append("W")
            elif team_score == opp_score:
                form.append("D")
            else:
                form.append("L")
        return form

    kickoff = row.kickoff_time
    if kickoff.tzinfo is None:
        kickoff = kickoff.replace(tzinfo=timezone.utc)

    now_utc = datetime.now(timezone.utc)

    if row.period == "FULLTIME":
        status = "finished"
    elif row.period == "PREMATCH" and kickoff <= now_utc <= kickoff + timedelta(minutes=300):
        status = "live"
    else:
        status = "upcoming"

    home = {
            "teamId": row.home_team_id,
            "teamName": row.home_team_name_en if locale == "en-US" else row.home_team_name_kr,
            "leaguePosition": row.home_position,
            "recentForm": get_recent_form(row.home_team_stat_id, kickoff),
    }

    away = {
            "teamId": row.away_team_id,
            "teamName": row.away_team_name_en if locale == "en-US" else row.away_team_name_kr,
            "leaguePosition": row.away_position,
            "recentForm": get_recent_form(row.away_team_stat_id, kickoff),
    }

    fixture = {
            "id": row.id,
            "matchweek": row.game_week,
            "kickoff": kickoff.isoformat(),
            "venue": row.name_en if locale == "en-US" else row.name_kr,
            "city": row.city_name_en if locale == "en-US" else row.city_name_kr,
            "status": status,
            "home" : home,
            "away" : away,
            "attendance" : row.attendance
        }

    if status == "finished":
        fixture["referee"] = {
                "main": row.referee_main_en if locale == "en-US" else row.referee_main_kr,
                "assist1": row.referee_a1_en if locale == "en-US" else row.referee_a1_kr,
                "assist2": row.referee_a2_en if locale == "en-US" else row.referee_a2_kr,
                "fourth": row.referee_4th_en if locale == "en-US" else row.referee_4th_kr,
        }

    return {
        "fixture" : fixture
    }
