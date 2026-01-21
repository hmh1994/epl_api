from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from database import get_db
from datetime import datetime, timedelta, timezone
from collections import defaultdict

from utils.leagues_util import LEAGUE_ENUM_MAP, get_competition_id
from utils.seasons_util import (
    web_to_db_season,
    get_season_id_by_abbr,
    get_current_or_latest_season_id
)

router = APIRouter(prefix="/api/v1", tags=["fetch_match_schedule"])
@router.get("/leagues/{leagueName}/matches")
def fetch_match_schedule(
    leagueName: str,
    season: Optional[str] = Query(None, description="If no season is provided, the default value is the latest season"),
    locale: Optional[str] = Query("en-US", description="support only ko-KR, en-US"),
    matchweek: Optional[int] = Query(1, ge=1),
    db: Session = Depends(get_db),
):
    ## 1. 리그
    competition_id, error = get_competition_id(db, leagueName)
    if error:
        return {"error": error}

    ## 2. 시즌
    if season:
        season_db = web_to_db_season(season)
        season_id = get_season_id_by_abbr(db, competition_id, season_db)
        if not season_id:
            return {"error": f"Season not found: {season}"}
    else:
        season_id = get_current_or_latest_season_id(db, competition_id)
        if not season_id:
            return {"error": "No season data found"}

    sql = text("""
        select 
            fx.kickoff_time,
            fx.id,
            fx.game_week,
            gr.name_en,
            gr.name_kr,
            gr.city_name_en,
            gr.city_name_kr,
            ma.period,
            of.display_name_en,
            of.display_name_kr,

            ma.home_team_id,
            ht.name_en AS home_team_name_en,
            ht.name_kr AS home_team_name_kr,
            hts.overall_posistion AS home_overall_position,
            ma.home_team_score,
            ma.away_team_id,
            at.name_en AS away_team_name_en,
            at.name_kr AS away_team_name_kr,
            ats.overall_posistion AS away_overall_position,
            ma.away_team_score
        from fixtures fx
        JOIN grounds gr ON fx.ground_id = gr.id
        JOIN matches ma ON fx.id = ma.fixture_id
        LEFT JOIN officials of ON ma.official_main_referee_id = of.id
        JOIN teams ht ON ma.home_team_id = ht.id
        JOIN teams at ON ma.away_team_id = at.id
        JOIN team_stats hts ON ma.home_team_id = hts.id
        JOIN team_stats ats ON ma.away_team_id = ats.id
        where fx.season_id = :season_id and fx.game_week = :matchweek
        order by fx.kickoff_time
    """)
    rows = db.execute(sql, {"season_id": season_id, "matchweek": matchweek}).fetchall()

    grouped = defaultdict(list)
    now_utc = datetime.now(timezone.utc)
    for row in rows:
        kickoff_utc = row.kickoff_time
        if row.period == "FULLTIME":
            status = "finished"

        elif (
            row.period == "PREMATCH"
            and kickoff_utc <= now_utc <= kickoff_utc + timedelta(minutes=300)
        ):
            status = "live"

        else:
            status = "upcoming"

        date_str = row.kickoff_time.date().isoformat()
        
        fixture = {
            "id": row.id,
            "matchweek": row.game_week,
            "kickoff": kickoff_utc.isoformat(),
            "venue": row.name_en if locale == "en-US" else row.name_kr,
            "city": row.city_name_en if locale == "en-US" else row.city_name_kr,
            "status": status
        }

        # finished 경기에서만 referee 포함
        if status == "finished" and row.display_name_en:
            fixture["referee"] = (
                row.display_name_en if locale == "en-US" else row.display_name_kr
            )

        home_data = {
            "teamdId": row.home_team_id,
            "teamdName": row.home_team_name_en if locale == "en-US" else row.home_team_name_kr,
            "position" : row.home_overall_position
        }   
        away_data = {
            "teamId": row.away_team_id,
            "teamdName": row.away_team_name_en if locale == "en-US" else row.away_team_name_kr,
            "position" : row.away_overall_position
        } 

        if status == "finsihed" :
            home_data["score"] = row.home_team_score
            away_data["score"] = row.away_team_score

        grouped[date_str].append(fixture)
        grouped[date_str].append(home_data)
        grouped[date_str].append(away_data)

    # 최종 data 구조
    data = []
    for date, fixtures in grouped.items():
        data.append({
            "date": date,
            "fixtures": fixtures,
            "home" : home_data,
            "away" : away_data
        })

    KST = timezone(timedelta(hours=9))
    last_updated = datetime.now(KST).strftime("%Y-%m-%dT%H:%M:%S")

    return {
        "data": data,
        "meta": {
            "leagueName": leagueName,
            "leagueId": competition_id,
            "season": season_id,
            "lastUpdated": last_updated,
            "locale": locale,
        }
    }