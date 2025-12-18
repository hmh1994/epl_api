from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from datetime import datetime, timedelta, timezone
from database import get_db

from utils.leagues_util import LEAGUE_ENUM_MAP, get_competition_id
from utils.seasons_util import (
    web_to_db_season,
    get_season_id_by_abbr,
    get_current_or_latest_season_id
)

router = APIRouter(prefix="/api/v1", tags=["fetch_player_detail"])

@router.get("/leagues/{leagueName}/player/{playerId}")
def fetch_player_detail(
    leagueName: str,
    playerId: str,
    season: Optional[str] = Query(None, description="If no season is provided, the default value is the latest season"),
    locale: Optional[str] = Query("en-US", description="support only ko-KR, en-US"),
    db: Session = Depends(get_db),
): 
    ## 리그 정보 조회
    competition_id, error = get_competition_id(db, leagueName)
    if error:
        return {"error": error}

    ## 시즌 정보 조회
    if season:  
        season_db = web_to_db_season(season)
        season_id = get_season_id_by_abbr(db, competition_id, season_db)
        if not season_id:
            return {"error": f"Season not found: {season}"}
    else:
        season_id = get_current_or_latest_season_id(db, competition_id)
        if not season_id:
            return {"error": "No season data found"}

    sql = """
        SELECT 
            p.id,
            p.display_name_en,
            p.display_name_kr,
            ps.team_id,
            p.position,
            p.photo_url,
            p.nationality_en,
            p.nationality_kr,
            DATE_PART('year', AGE(CURRENT_DATE, p.birth_date)) AS age,
            p.height,
            p.weight,
            ps.shooting_goals,
            ps.passing_assists,
            ps.appearances
        FROM players p
        JOIN player_stats ps ON p.id = ps.player_id
        WHERE ps.season_id = :season_id
        AND p.id = :player_id
    """
    params = {
        "season_id": season_id,
        "player_id": playerId,
    }
    rows = db.execute(text(sql), params).fetchone()

    name = row.display_name_en if locale == "en-US" else row.display_name_kr
    nationality = row.nationality_en if locale == "en-US" else row.nationality_kr

    data = {
        "summary": {
            "id": row.id,
            "name": name,
            "teamId": row.team_id,
            "position": row.position,
            "photo": row.photo_url,
            "nationality": nationality,
            "age": row.age,
            "height": row.height,
            "weight": row.weight,
        },
        "attributes": {
            "pace": None,
            "shooting": None,
            "passing": None,
            "dribbling": None,
            "defending": None,
            "physical": None,
        },
        "performance": {
            "goals": row.shooting_goals,
            "assists": row.passing_assists,
            "pace": None,
            "matches": row.appearances,
        }
    }
    '''field = []
    for row in rows:
        field.append({
            "id" : row.id,
            "name": row.display_name_en if locale == "en-US" else row.display_name_kr,
            "teamId": row.team_id,
            "position": row.position,
            "photo":  row.photo_url,
            "nationality": row.nationality_en if locale == "en-US" else row.nationality_kr,
            "age": row.age,
            "height": row.height,
            "weight" : row.weight,
            "pace" : None,
            "shooting" : None,
            "passing" :  None,
            "dribbling" :  None,
            "defending" : None,
            "physical" : None,
            "goals" : row.shooting_goals,
            "assists" : row.passing_assists,
            "pace2" : None,
            "year" : season,
            "teamId2" : row.team_id,
            "matches" : row.appearances,
            "goals2" : row.shooting_goals
        })
    '''
    KST = timezone(timedelta(hours=9))
    #last_updated = datetime.now(KST).isoformat()
    last_updated = datetime.now(KST).strftime("%Y-%m-%dT%H:%M:%S")
    return {
        "data" : data,
        "meta" : {
            "leagueName": leagueName,
            "leagueId": competition_id,
            "season" : season_id,
            "lastUpdated" : last_updated,
            "locale" : locale,
        }
    }