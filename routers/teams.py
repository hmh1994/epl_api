from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from crud.team import get_teams
from schemas.team import TeamsInfoResponse

router = APIRouter(prefix="/api/v1", tags=["teams"])

@router.get("/teams", response_model=TeamsInfoResponse)
def read_teams(
    leagueId: str = Query(None),
    search: str = Query(None),
    db: Session = Depends(get_db)
):
    return get_teams(db, leagueId, search)