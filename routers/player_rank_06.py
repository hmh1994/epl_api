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
    season: Optional[str] = Query(None),
    locale: Optional[str] = Query("en-US"),
    category: Optional[str] = Query("top-scorers", regex="^(top-scorers|assists)$"),
    limit: Optional[int] = Query(10),
    db: Session = Depends(get_db),
):
    # 1. 리그 정보 조회
    competition_id, error = get_competition_id(db, leagueId)
    if error:
        return {"error": error}

    # 2. 시즌 정보 조회
    if season:
        season_db = web_to_db_season(season)
        season_id = get_season_id_by_abbr(db, competition_id, season_db)
        if not season_id:
            return {"error": f"Season not found: {season}"}
    else:
        season_id = get_current_or_latest_season_id(db, competition_id)
        if not season_id:
            return {"error": "No season data found"}

    # 3. 선수 랭킹 조회
    if category == "top-scorers":
        order_by = "ps.shooting_goals DESC, ps.shooting_goals_penalty DESC"
    else:  # assists
        order_by = "ps.passing_assists DESC"

    sql = f"""
        SELECT 
            p.id AS player_id,
            CASE WHEN :locale = 'ko-KR' THEN p.display_name_kr ELSE p.display_name_en END AS name,
            ps.team_id,
            ps.shooting_goals AS goals,
            ps.passing_assists AS assists,
            NULL AS rating
        FROM player_stats ps
        JOIN players p ON ps.player_id = p.id
        WHERE ps.season_id = :season_id
        ORDER BY {order_by}
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
            "rating": row._mapping["rating"]
        })

    return {
        "players": rankings,
        "meta": {
            "leagueId": competition_id,
            "season": season_id,
            "category": category,
            "source": "player_stats",
            "locale": locale
        }
    }
