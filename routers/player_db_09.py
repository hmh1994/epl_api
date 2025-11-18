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

router = APIRouter(prefix="/api/v1", tags=["player_db_09"])

@router.get("/leagues/{leagueId}/players/database")
def get_player_database(
    leagueId: str,
    season: Optional[str] = Query(None, description = "If no season is provided, the default value is the latest season"),
    locale: Optional[str] = Query("en-US", description = "support only ko-KR, en-US"),
    teamId: Optional[str] = Query(None),
    position: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    ageMin: Optional[int] = Query(None),
    ageMax: Optional[int] = Query(None),
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





      # --------------------------------------------------------
    # 3. Filters 조회 (positions / teamIds / nationalities / ageRange)
    # --------------------------------------------------------
    filters_sql = text("""
        SELECT 
            ARRAY_AGG(DISTINCT p.position) AS positions,
            ARRAY_AGG(DISTINCT ps.team_id) AS team_ids,
            ARRAY_AGG(DISTINCT p.nationality_en) AS nationalities_en,
            ARRAY_AGG(DISTINCT p.nationality_kr) AS nationalities_kr,
            MIN(DATE_PART('year', AGE(CURRENT_DATE, p.birth_date))) AS min_age,
            MAX(DATE_PART('year', AGE(CURRENT_DATE, p.birth_date))) AS max_age
        FROM players p
        LEFT JOIN player_stats ps
            ON ps.player_id = p.id
            AND ps.season = :season_id
        WHERE p.competition_id = :competition_id
    """)

    f = db.execute(filters_sql, {
        "competition_id": competition_id,
        "season_id": season_id,
    }).fetchone()

    filters = {
        "positions": f.positions or [],
        "teamIds": f.team_ids or [],
        "nationalities": (f.nationalities_kr if locale == "ko-KR" else f.nationalities_en) or [],
        "ageRange": {
            "min": int(f.min_age) if f.min_age is not None else None,
            "max": int(f.max_age) if f.max_age is not None else None,
        }
    }

    # --------------------------------------------------------
    # 4. Player + Stats 조회
    # --------------------------------------------------------
    sql = text("""
        WITH base AS (
            SELECT 
                p.id,
                p.display_name_en,
                p.display_name_kr,
                p.photo_url,
                p.position,
                DATE_PART('year', AGE(CURRENT_DATE, p.birth_date)) AS age,
                p.nationality_en,
                p.nationality_kr,
                p.height,
                p.weight
            FROM players p
            WHERE p.competition_id = :competition_id
        )
        SELECT 
            b.id,
            b.display_name_en,
            b.display_name_kr,
            b.photo_url,
            b.position,
            b.age,
            b.nationality_en,
            b.nationality_kr,
            b.height,
            b.weight,
            ps.team_id,
            ps.shooting_goals AS goals,
            ps.passing_assists AS assists
        FROM base b
        LEFT JOIN player_stats ps
            ON ps.player_id = b.id
            AND ps.season = :season_id
        WHERE 1 = 1
            AND (:team_id IS NULL OR ps.team_id = :team_id)
            AND (:position IS NULL OR b.position = :position)
            AND (
                :search IS NULL OR
                b.display_name_en ILIKE '%' || :search || '%' OR
                b.display_name_kr ILIKE '%' || :search || '%'
            )
            AND (:age_min IS NULL OR b.age >= :age_min)
            AND (:age_max IS NULL OR b.age <= :age_max)
        ORDER BY b.id
    """)

    rows = db.execute(sql, {
        "competition_id": competition_id,
        "season_id": season_id,
        "team_id": teamId,
        "position": position,
        "search": search,
        "age_min": ageMin,
        "age_max": ageMax,
    }).fetchall()

    players = []
    for r in rows:
        players.append({
            "id": r.id,
            "name": r.display_name_kr if locale == "ko-KR" else r.display_name_en,
            "photo": r.photo_url,
            "teamId": r.team_id,
            "position": r.position,
            "age": int(r.age) if r.age is not None else None,
            "nationality": r.nationality_kr if locale == "ko-KR" else r.nationality_en,
            "height": r.height,
            "weight": r.weight,
            "goals": r.goals,
            "assists": r.assists,
            "stats": {},       # TODO: SkillSet 이후 확장
            "career": []       # TODO: Career 이후 확장
        })

    # --------------------------------------------------------
    # 5. 최종 응답 조립
    # --------------------------------------------------------
    return {
        "meta": {
            "leagueId": competition_id,
            "season": season_id,
            "lastUpdated": 0
        },
        "resource": {
            "players": players,
            "filters": filters
        }
    }