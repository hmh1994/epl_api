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

            main_ref.display_name_en   AS referee_main_en,
            main_ref.display_name_kr   AS referee_main_kr,
            a1_ref.display_name_en     AS referee_a1_en,
            a1_ref.display_name_kr     AS referee_a1_kr,
            a2_ref.display_name_en     AS referee_a2_en,
            a2_ref.display_name_kr     AS referee_a2_kr,
            fourth_ref.display_name_en AS referee_4th_en,
            fourth_ref.display_name_kr AS referee_4th_kr,
            ht.name_en AS home_team_name_en,
            ht.name_kr AS home_team_name_kr,
            at.name_en AS away_team_name_en,
            at.name_kr AS away_team_name_kr,
            ma.home_team_id,
            hts.id AS home_team_stat_id,
            hts.overall_position AS home_position,
            ma.home_team_score,

            ma.away_team_id,
            ats.id AS away_team_stat_id,
            ats.overall_position AS away_position,
            ma.away_team_score
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

    return {
        "data": dict(row._mapping)  # ✅ 핵심 수정
    }
