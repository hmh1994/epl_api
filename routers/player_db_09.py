from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from database import get_db

router = APIRouter(prefix="/api/v1", tags=["player_db_09"])

@router.get("/leagues/{leagueId}/players/database")
def get_player_database(
    leagueId: str,
    season: Optional[str] = Query(None),
    locale: Optional[str] = Query("ko-KR"),
    teamId: Optional[str] = Query(None),
    position: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    ageMin: Optional[int] = Query(None),
    ageMax: Optional[int] = Query(None),
    db: Session = Depends(get_db),
):
    sql = text("SELECT * FROM teams")
    result = db.execute(sql).fetchall()
    return [dict(row._mapping) for row in result]