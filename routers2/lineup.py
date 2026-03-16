from collections import defaultdict
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from database import get_db

from utils.leagues_util import LEAGUE_ENUM_MAP, get_competition_id
from utils.seasons_util import (
    web_to_db_season,
    get_season_id_by_abbr,
    get_current_or_latest_season_id
)

router = APIRouter(prefix="/api/v1", tags=["fetch_match_lineup"])

@router.get("/leagues/{leagueName}/matches/{matchId}/lineup")
def fetch_match_detail(
    leagueName: str,
    matchId: str,
    season: Optional[str] = Query(None),
    locale: Optional[str] = Query("en-US"),
    db: Session = Depends(get_db),
):
    return 0