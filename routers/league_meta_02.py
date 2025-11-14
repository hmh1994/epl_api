from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from database import get_db

router = APIRouter(prefix="/api/v1", tags=["league_meta_02"])

@router.get("/leagues/{leagueId}/metadata")
def get_league_metadata(
    leagueId: str,
    season: Optional[str] = Query(None),
    locale: Optional[str] = Query("ko-KR"),
    db: Session = Depends(get_db),
):
    sql = text("SELECT * FROM teams")
    result = db.execute(sql).fetchall()
    return [dict(row._mapping) for row in result]