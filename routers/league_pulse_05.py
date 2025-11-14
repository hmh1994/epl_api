from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from database import get_db

router = APIRouter(prefix="/api/v1", tags=["league_pulse_05"])

@router.get("/leagues/{leagueId}/meta")
def get_league_meta(
    leagueId: str,
    season: Optional[str] = Query(None),
    locale: Optional[str] = Query("ko-KR"),
    db: Session = Depends(get_db),
):
    sql = text("SELECT * FROM teams")
    result = db.execute(sql).fetchall()
    return [dict(row._mapping) for row in result]