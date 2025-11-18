from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from database import get_db
from utils.leagues_util import get_competition_id
from utils.seasons_util import web_to_db_season, get_season_id_by_abbr, get_current_or_latest_season_id

router = APIRouter(prefix="/api/v1", tags=["player_rankings_06"])

@router.get("/leagues/{leagueId}/player-rankings")
def get_player_rankings(
    leagueId: str,
    season: Optional[str] = Query(None, description="If no season is provided, the default value is the latest season"),
    locale: Optional[str] = Query("en-US", description="support only ko-KR, en-US"),
    category: Optional[str] = Query("top-scorers", description='top-scorers or assists'),
    limit: Optional[int] = Query(10, description="Number of top players to return"),
    db: Session = Depends(get_db),
):
    # 리그 정보 조회
    competition_id, error = get_competition_id(db, leagueId)
    if error:
        return {"error": error}

    # 시즌 정보 조회
    if season:
        season_db = web_to_db_season(season)
        season_id = get_season_id_by_abbr(db, competition_id, season_db)
        if not season_id:
            return {"error": f"Season not found: {season}"}
    else:
        season_id = get_current_or_latest_season_id(db, competition_id)
        if not season_id:
            return {"error": "No season data found"}

    # 정렬 기준 결정
    if category == "assists":
        order_by = "COALESCE(ps.passing_assists::int, 0) DESC"
    else:  # top-scorers
        order_by = "COALESCE(ps.shooting_goals::int, 0) DESC"

    # 선수 랭킹 쿼리
    sql = f"""
        SELECT * FROM (
            SELECT
                p.id AS player_id,
                CASE WHEN :locale = 'ko-KR' THEN p.display_name_kr ELSE p.display_name_en END AS name,
                ps.team_id,
                COALESCE(ps.shooting_goals::int, 0) AS goals,
                COALESCE(ps.passing_assists::int, 0) AS assists,
                ROW_NUMBER() OVER (ORDER BY {order_by}) AS ranking
            FROM player_stats ps
            JOIN players p ON ps.player_id = p.id
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

    rankings = []
    for row in rows:
        rankings.append({
            "name": row._mapping["name"],
            "teamId": row._mapping["team_id"],
            "goals": row._mapping["goals"],
            "assists": row._mapping["assists"],
            "ranking": row._mapping["ranking"]
        })

    return {
        "players": rankings,
        "meta": {
            "leagueId": competition_id,
            "season": season_id,
            "category": category,
        }
    }
