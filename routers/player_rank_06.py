from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from database import get_db

router = APIRouter(prefix="/api/v1", tags=["player_rank_06"])

@router.get("/leagues/{leagueId}/player-rankings")
def get_player_rankings(
    leagueId: str,
    season: Optional[str] = Query(None),
    locale: Optional[str] = Query("ko-KR"),
    category: Optional[str] = Query("top-scorers"),
    limit: Optional[int] = Query(10),
    db: Session = Depends(get_db),
):
    sql = text("SELECT * FROM teams")
    result = db.execute(sql).fetchall()
    return [dict(row._mapping) for row in result]
