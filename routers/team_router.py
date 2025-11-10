from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from services.team_service import get_teams

router = APIRouter(prefix="/api/v1/teams")

@router.get("")
def teams(
    leagueId: str = Query(None),
    search: str = Query(None),
    db: Session = Depends(get_db)
):
    data = get_teams(db, leagueId, search)
    meta = {"total": len(data), "leagueId": leagueId}
    return {"data": data, "meta": meta}
