from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from database import get_db

router = APIRouter(prefix="/api/v1", tags=["team_info_01.py"])

@router.get("/teams")
def get_teams(
    leagueId: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    season: Optional[str] = Query(None),
    locale: Optional[str] = Query("ko-KR"),
    db: Session = Depends(get_db),
):
    sql = text("SELECT * FROM teams")
    result = db.execute(sql).fetchall()
    return [dict(row._mapping) for row in result]