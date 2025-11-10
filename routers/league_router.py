from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from database import get_db
from services.league_service import get_league_metadata

router = APIRouter(prefix="/api/v1/leagues")

@router.get("/{league_id}/metadata")
def league_metadata(
    league_id: str,
    season: str = Query(...),
    db: Session = Depends(get_db),
):
    data = get_league_metadata(db, league_id, season)
    if not data:
        return {"data": None, "meta": {"leagueId": league_id, "season": season}}
    return {"data": data, "meta": {"leagueId": league_id, "season": season}}