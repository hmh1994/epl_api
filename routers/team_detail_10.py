from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from database import get_db

router = APIRouter(prefix="/api/v1", tags=["team_detail_10"])

@router.get("/leagues/{leagueId}/teams/profiles")
def get_team_profiles(
    leagueId: str,
    season: Optional[str] = Query(None),
    locale: Optional[str] = Query("ko-KR"),
    search: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    sql = text("SELECT * FROM teams")
    result = db.execute(sql).fetchall()
    return [dict(row._mapping) for row in result]

@router.get("/teams/{teamId}/squad")
def get_team_squad(
    teamId: str,
    season: Optional[str] = Query(None),
    locale: Optional[str] = Query("ko-KR"),
    db: Session = Depends(get_db),
):
    sql = text("SELECT * FROM teams")
    result = db.execute(sql).fetchall()
    return [dict(row._mapping) for row in result]