from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from database import get_db

from utils.leagues_util import get_competition_id
from utils.seasons_util import (
    web_to_db_season,
    get_season_id_by_abbr,
    get_current_or_latest_season_id
)

router = APIRouter(prefix="/api/v1", tags=["fetch_match_lineup"])

KST = timezone(timedelta(hours=9))


@router.get("/leagues/{leagueName}/fixtures/{fixtureId}/lineup")
def fetch_match_lineup(
    leagueName: str,
    fixtureId: str,
    season: Optional[str] = Query(None),
    locale: Optional[str] = Query("en-US"),
    db: Session = Depends(get_db),
):

    # ---------------------------
    # 리그 조회
    # ---------------------------

    competition_id, error = get_competition_id(db, leagueName)
    if error:
        return {"error": error}

    # ---------------------------
    # 시즌 조회
    # ---------------------------

    if season:
        season_db = web_to_db_season(season)
        season_id = get_season_id_by_abbr(db, competition_id, season_db)
        if not season_id:
            return {"error": f"Season not found: {season}"}
    else:
        season_id = get_current_or_latest_season_id(db, competition_id)
        if not season_id:
            return {"error": "No season data found"}

    # ---------------------------
    # 1️⃣ fixture → match 조회
    # ---------------------------

    match_sql = text("""
        SELECT 
            ma.id AS match_id,
            ma.home_team_formation,
            ma.away_team_formation,
            ma.home_team_captain_id,
            ma.away_team_captain_id,
            ma.home_team_id,
            ma.away_team_id
        FROM fixtures fx
        JOIN matches ma ON fx.id = ma.fixture_id
        WHERE fx.id = :fixture_id
    """)

    match_row = db.execute(match_sql, {"fixture_id": fixtureId}).fetchone()

    if not match_row:
        return {"error": "Match not found"}

    match_id = match_row.match_id

    # ---------------------------
    # 2️⃣ lineup
    # ---------------------------

    lineup_sql = text("""
        SELECT
            mla.match_id,
            mla.player_id,
            mla.is_home,
            mla.position,
            mla.shirt_number,
            mla.row,
            mla.column,
            p.display_name_kr,
            p.display_name_en,
            p.photo_url
        FROM match_lineup_association mla
        LEFT JOIN players p ON mla.player_id = p.id
        WHERE mla.match_id = :match_id
        ORDER BY mla.is_home DESC, mla.row, mla.column
    """)

    lineup_rows = db.execute(lineup_sql, {"match_id": match_id}).fetchall()

    lineup = []

    for r in lineup_rows:
        lineup.append({
            "matchId": r.match_id,
            "playerId": r.player_id,
            "isHome": r.is_home,
            "position": r.position,
            "shirtNumber": r.shirt_number,
            "row": r.row,
            "column": r.column,
            "playerName": r.display_name_en if locale == "en-US" else r.display_name_kr,
            "photoUrl": r.photo_url
        })

    # ---------------------------
    # 3️⃣ substitutes
    # ---------------------------

    sub_sql = text("""
        SELECT
            msa.match_id,
            msa.player_id,
            msa.is_home,
            msa.position,
            msa.shirt_number,
            p.display_name_kr,
            p.display_name_en,
            p.photo_url
        FROM match_substitute_association msa
        LEFT JOIN players p ON msa.player_id = p.id
        WHERE msa.match_id = :match_id
    """)

    sub_rows = db.execute(sub_sql, {"match_id": match_id}).fetchall()

    substitutes = []

    for r in sub_rows:
        substitutes.append({
            "matchId": r.match_id,
            "playerId": r.player_id,
            "isHome": r.is_home,
            "position": r.position,
            "shirtNumber": r.shirt_number,
            "playerName": r.display_name_en if locale == "en-US" else r.display_name_kr,
            "photoUrl": r.photo_url
        })

    # ---------------------------
    # 4️⃣ substitutions
    # ---------------------------

    sub_event_sql = text("""
        SELECT
            msa.match_id,
            msa.in_player_id,
            msa.out_player_id,
            msa.is_home,
            msa.clock
        FROM match_substitution_association msa
        WHERE msa.match_id = :match_id
        ORDER BY msa.clock
    """)

    sub_event_rows = db.execute(sub_event_sql, {"match_id": match_id}).fetchall()

    substitutions = []

    for r in sub_event_rows:
        substitutions.append({
            "matchId": r.match_id,
            "inPlayerId": r.in_player_id,
            "outPlayerId": r.out_player_id,
            "isHome": r.is_home,
            "clock": r.clock
        })

    # ---------------------------
    # 5️⃣ team colors
    # ---------------------------

    color_sql = text("""
        SELECT
            ht.color_primary AS home_primary,
            ht.color_secondary AS home_secondary,
            at.color_primary AS away_primary,
            at.color_secondary AS away_secondary
        FROM fixtures ma
        LEFT JOIN teams ht ON ma.home_team_id = ht.id
        LEFT JOIN teams at ON ma.away_team_id = at.id
        WHERE ma.id = :fixture_id
    """)

    color_row = db.execute(color_sql, {"fixture_id": fixtureId}).fetchone()

    team_colors = {
        "homePrimary": color_row.home_primary if color_row else None,
        "homeSecondary": color_row.home_secondary if color_row else None,
        "awayPrimary": color_row.away_primary if color_row else None,
        "awaySecondary": color_row.away_secondary if color_row else None
    }

    # ---------------------------
    # 최종 data
    # ---------------------------

    data = {
        "homeFormation": match_row.home_team_formation,
        "awayFormation": match_row.away_team_formation,
        "homeCaptainId": match_row.home_team_captain_id,
        "awayCaptainId": match_row.away_team_captain_id,
        "lineup": lineup,
        "substitutes": substitutes,
        "substitutions": substitutions,
        "teamColors": team_colors
    }

    return {
        "data": data,
        "meta": {
            "matchId": match_id,
            "fixtureId": fixtureId,
            "season": season_id,
            "locale": locale,
            "lastUpdated": datetime.now(KST).strftime("%Y-%m-%dT%H:%M:%S")
        }
    }