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

router = APIRouter(prefix="/api/v1", tags=["fetch_player_list"])
@router.get("/leagues/{leagueName}/player")
def fetch_player_list(
    leagueName: str,
    season: Optional[str] = Query(None, description = "If no season is provided, the default value is the latest season"),
    locale: Optional[str] = Query("en-US", description = "support only ko-KR, en-US"),
    teamId: Optional[str] = Query(None),
    position: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
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

    ## 시즌 정보로 조회되는 team_id 추출
    sql_team_ids = text("""
        SELECT team_id
        FROM team_stats
        WHERE season_id = :season_id
    """)
    team_rows = db.execute(sql_team_ids, {"season_id": season_id}).fetchall()
    team_ids = [row.team_id for row in team_rows]

    KST = timezone(timedelta(hours=9))
    last_updated = datetime.now(KST).strftime("%Y-%m-%dT%H:%M:%S")
    if not team_ids:
        return {
            "data": [],
            "meta": {
                "leagueName": leagueName,
                "leagueId" : competition_id,
                "season" : season_id,
                "locale" : locale,
                "lastUpdated" : last_updated,
            }
        }

    # -----------------------------------
    # 4. 실제 선수 데이터 조회 (players + player_stats JOIN)
    # -----------------------------------
    sql_players = f"""
        SELECT 
            p.id,
            p.display_name_en,
            p.display_name_kr,
            ps.team_id,
            t.name_en AS team_name_en,
            t.name_kr AS team_name_kr,
            p.position,
            p.photo_url,
            p.nationality_en,
            p.nationality_kr,
            DATE_PART('year', AGE(CURRENT_DATE, p.birth_date)) AS age,
            p.height,
            p.weight,
            ps.shooting_goals,
            ps.passing_assists
        FROM players p
        JOIN player_stats ps 
            ON p.id = ps.player_id
        JOIN teams t
            ON ps.team_id = t.id
        WHERE ps.season_id = :season_id
        AND ps.team_id = ANY(:team_ids)
    """
    params = {
        "season_id": season_id,
        "team_ids": team_ids,
    }

    # -----------------------------------
    # 5. 필터 적용
    # -----------------------------------
    if teamId:
        sql_players += " AND ps.team_id = :teamId"
        params["teamId"] = teamId

    if position:
        sql_players += " AND p.position = :position"
        params["position"] = position

    if search:
        sql_players += """
            AND (
                p.display_name_en ILIKE :search
                OR p.display_name_kr ILIKE :search
                OR p.full_name ILIKE :search
            )
        """
        params["search"] = f"%{search}%"

    rows = db.execute(text(sql_players), params).fetchall()

    # -----------------------------------
    # 6. 로케일 적용 + null 처리
    # -----------------------------------
    players = []
    for row in rows:
        players.append({
            "id": row.id,
            "name": row.display_name_en if locale == "en-US" else row.display_name_kr,
            "photo": row.photo_url,
            "teamId": row.team_id,
            "teamName" : row.team_name_en if locale == "en-US" else row.team_name_kr,
            "position": row.position,
            "age": row.age,
            "nationality": row.nationality_en if locale == "en-US" else row.nationality_kr,
            "height": row.height,
            "weight": row.weight,
            "goals": row.shooting_goals or 0,
            "assists": row.passing_assists or 0,
            "pace": None,
            "passing" : None
        })
    '''
        sql_filters = text("""
            SELECT 
                ARRAY(
                    SELECT DISTINCT position 
                    FROM players
                    WHERE position IS NOT NULL 
                ) AS positions,
                ARRAY(
                    SELECT DISTINCT team_id 
                    FROM player_stats 
                    WHERE season_id = :season_id
                ) AS team_ids,
                ARRAY(
                    SELECT DISTINCT nationality_en
                    FROM players
                    WHERE nationality_en IS NOT NULL
                ) AS nationalities
        """)

        filter_row = db.execute(sql_filters, {"season_id": season_id}).fetchone()

        filters = {
            "positions": filter_row.positions,
            "teamIds": filter_row.team_ids,
            "nationalities": filter_row.nationalities,
        }
    '''

    # -----------------------------------
    # 8. 최종 반환
    # -----------------------------------
    return {
        "data": players,
        "meta": {
                "leagueName": leagueName,
                "leagueId" : competition_id,
                "season" : season_id,
                "locale" : locale,
                "lastUpdated" : last_updated,
            }
    }