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

router = APIRouter(prefix="/api/v1", tags=["fetch_race"])
@router.get("/leagues/{leagueName}/players/race")
def fetch_scoring_race(
    leagueName: str,
    season: Optional[str] = Query(None, description="If no season is provided, the default value is the latest season"),
    category: Optional[str] = Query("goal", description="goal | assist | point | xg"),
    locale: Optional[str] = Query("en-US", description="support only ko-KR, en-US"),
    limit: Optional[int] = Query(10, description="1~30"),
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

    ## 3. category → ORDER BY 수식 매핑
    category_order_map = {
        "goal": "COALESCE(ps.shooting_goals, 0)",
        "assist": "COALESCE(ps.passing_assists, 0)",
        "point": "COALESCE(ps.shooting_goals, 0) + COALESCE(ps.passing_assists, 0)",
        "xg": "COALESCE(ps.shooting_expected_goals_non_penalty, 0)"
    }

    order_expr = category_order_map.get(category)
    if not order_expr:
        return {"error": f"Invalid category: {category}"}

    ## 4. SQL
    sql = f"""
        SELECT * FROM (
            SELECT
                p.id,
                CASE 
                    WHEN :locale = 'ko-KR' THEN p.display_name_kr 
                    ELSE p.display_name_en 
                END AS name,
                ps.team_id,
                CASE 
                    WHEN :locale = 'ko-KR' THEN t.name_kr 
                    ELSE t.name_en 
                END AS team_name,
                COALESCE(ps.shooting_goals, 0) AS goals,
                COALESCE(ps.passing_assists, 0) AS assists,
                (COALESCE(ps.shooting_goals, 0) + COALESCE(ps.passing_assists, 0)) AS points,
                COALESCE(ps.shooting_expected_goals_non_penalty, 0) AS xg,
                p.photo_url,
                ps.score_overall,
                ROW_NUMBER() OVER (
                    ORDER BY
                        {order_expr} DESC,
                        COALESCE(ps.shooting_goals, 0) DESC,
                        COALESCE(ps.passing_assists, 0) DESC
                ) AS ranking
            FROM player_stats ps
            JOIN players p ON ps.player_id = p.id
            JOIN teams t ON ps.team_id = t.id
            WHERE ps.season_id = :season_id
        ) ranked
        LIMIT :limit
    """

    params = {
        "season_id": season_id,
        "limit": limit,
        "locale": locale
    }

    rows = db.execute(text(sql), params).fetchall()

    ## 5. 응답 데이터
    data = []
    for row in rows:
        data.append({
            "playerId": row.id,
            "name": row.name,
            "teamId": row.team_id,
            "teamName": row.team_name,
            "goals": row.goals,
            "assists": row.assists,
            "points": row.points,
            "xg": row.xg,
            "photo": row.photo_url,
            "rating": row.score_overall,
            "ranking" : row.ranking
        })

    return {
        "data": data,
        "meta": {
            "leagueName": leagueName,
            "leagueId": competition_id,
            "season": season_id,
            "locale": locale,
            "category": category
        }
    }

'''
@router.get("/leagues/{leagueName}/players/scoring-race")
def fetch_scoring_race(
    leagueName: str,
    season: Optional[str] = Query(None, description="If no season is provided, the default value is the latest season"),
    category: Optional[str] = Query("goal", description="goal | assist | point"),
    locale: Optional[str] = Query("en-US", description="support only ko-KR, en-US"),
    limit: Optional[int] = Query(10, description="1~30"),
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

    ## 3. category → 정렬 컬럼 매핑 (🔥 중요)
    category_order_map = {
        "goal": "ps.shooting_goals",
        "assist": "ps.passing_assists",
        "point": "ps.score_overall"
    }

    order_column = category_order_map.get(category)
    if not order_column:
        return {"error": f"Invalid category: {category}"}

    ## 4. SQL
    sql = f"""
        SELECT * FROM (
            SELECT
                p.id,
                CASE 
                    WHEN :locale = 'ko-KR' THEN p.display_name_kr 
                    ELSE p.display_name_en 
                END AS name,
                ps.team_id,
                CASE 
                    WHEN :locale = 'ko-KR' THEN t.name_kr 
                    ELSE t.name_en 
                END AS team_name,
                COALESCE(ps.shooting_goals, 0) AS goals,
                COALESCE(ps.passing_assists, 0) AS assists,
                COALESCE(ps.score_overall, 0) AS points,
                COALESCE(ps.shooting_expected_goals, 0) AS xg,
                p.photo_url,
                ROW_NUMBER() OVER (
                    ORDER BY 
                        COALESCE({order_column}, 0) DESC
                ) AS ranking
            FROM player_stats ps
            JOIN players p ON ps.player_id = p.id
            JOIN teams t ON ps.team_id = t.id
            WHERE ps.season_id = :season_id
        ) ranked
        LIMIT :limit
    """

    params = {
        "season_id": season_id,
        "limit": limit,
        "locale": locale
    }

    rows = db.execute(text(sql), params).fetchall()

    ## 5. 응답 데이터
    data = []
    for row in rows:
        data.append({
            "playerId": row.id,
            "name": row.name,
            "teamId": row.team_id,
            "teamName": row.team_name,
            "goals": row.goals,
            "assists": row.assists,
            "points": row.points,
            "xg": row.xg,
            "photo": row.photo_url,
            "ranking": row.ranking
        })

    return {
        "data": data,
        "meta": {
            "leagueName": leagueName,
            "leagueId": competition_id,
            "season": season_id,
            "locale": locale,
            "category": category
        }
    }
'''
'''
@router.get("/leagues/{leagueName}/players/scoring-race")
def fetch_scoring_race(
    leagueName: str,
    season: Optional[str] = Query(None, description="If no season is provided, the default value is the latest season"),
    
    locale: Optional[str] = Query("en-US", description="support only ko-KR, en-US"),
    limit: Optional[int] = Query(10, description="1~30"),
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
    
    sql = f"""
        SELECT * FROM (
            SELECT
                p.id,
                CASE WHEN :locale = 'ko-KR' THEN p.display_name_kr ELSE p.display_name_en END AS name,
                ps.team_id,
                CASE 
                    WHEN :locale = 'ko-KR' THEN t.name_kr 
                    ELSE t.name_en 
                END AS team_name,
                COALESCE(ps.shooting_goals::int, 0) AS goals,
                COALESCE(ps.passing_assists::int, 0) AS assists,
                p.photo_url,
                ROW_NUMBER() OVER (ORDER BY COALESCE(ps.shooting_goals::int, 0) DESC, COALESCE(ps.passing_assists::int, 0) DESC) AS ranking
            FROM player_stats ps
            JOIN players p ON ps.player_id = p.id
            JOIN teams t ON ps.team_id = t.id
            WHERE ps.season_id = :season_id
        ) ranked
        LIMIT :limit
    """
    params = {
        "season_id": season_id,
        "limit": limit,
        "locale": locale
    }

    rows = db.execute(text(sql), params).fetchall()

    field = []
    for row in rows:
        field.append({
            "playerId" : row._mapping["id"],
            "name": row._mapping["name"],
            "teamId": row._mapping["team_id"],
            "teamName": row._mapping["team_name"],
            "goals": row._mapping["goals"],
            "assists": row._mapping["assists"],
            "photo": row._mapping["photo_url"],
            "ranking": row._mapping["ranking"]
        })

    return {
        "data" : field,
        "meta" : {
            "leagueName": leagueName,
            "leagueId": competition_id,
            "season" : season_id,
            "locale" : locale,
            "category" : "goal"
        }
    }
'''