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

router = APIRouter(prefix="/api/v1", tags=["fetch_match_schedule"])

@router.get("/leagues/{leagueName}/matches")
def fetch_match_schedule(
    leagueName: str,
    season: Optional[str] = Query(None),
    locale: Optional[str] = Query("en-US"),
    startDate: Optional[str] = Query(None, example="2024-08-16"),
    endDate: Optional[str] = Query(None, example="2024-08-20"),
    db: Session = Depends(get_db),
):
    # 1. 리그
    competition_id, error = get_competition_id(db, leagueName)
    if error:
        return {"error": error}

    # 2. 시즌
    if season:
        season_db = web_to_db_season(season)
        season_id = get_season_id_by_abbr(db, competition_id, season_db)
        if not season_id:
            return {"error": f"Season not found: {season}"}
    else:
        season_id = get_current_or_latest_season_id(db, competition_id)
        if not season_id:
            return {"error": "No season data found"}

    # 날짜 기본값 처리
    if not startDate or not endDate:
        return {"error": "startDate and endDate are required"}

    # 3. 경기 조회 SQL
    sql = text("""
        SELECT 
            fx.kickoff_time,
            fx.id,
            fx.game_week,
            gr.name_en,
            gr.name_kr,
            gr.city_name_en,
            gr.city_name_kr,
            ma.period,

            of.display_name_en AS referee_en,
            of.display_name_kr AS referee_kr,

            ma.home_team_id,
            hts.overall_position AS home_position,
            ma.home_team_score,

            ma.away_team_id,
            ats.overall_position AS away_position,
            ma.away_team_score
        FROM fixtures fx
        JOIN grounds gr ON fx.ground_id = gr.id
        JOIN matches ma ON fx.id = ma.fixture_id
        LEFT JOIN officials of ON ma.official_main_referee_id = of.id
        LEFT JOIN team_stats hts ON ma.home_team_id = hts.team_id AND hts.season_id = :season_id
        LEFT JOIN team_stats ats ON ma.away_team_id = ats.team_id AND ats.season_id = :season_id
        WHERE fx.season_id = :season_id
          AND fx.kickoff_time::date BETWEEN :start_date AND :end_date
        ORDER BY fx.kickoff_time
    """)

    rows = db.execute(
        sql,
        {
            "season_id": season_id,
            "start_date": startDate,
            "end_date": endDate,
        }
    ).fetchall()

    # 4. 최근 5경기 form 조회 SQL
    form_sql = text("""
        SELECT
            tsma.is_home,
            m.home_team_score,
            m.away_team_score
        FROM team_stat_match_association tsma
        JOIN matches m ON tsma.match_id = m.id
        WHERE tsma.team_stat_id = :team_stat_id
        ORDER BY tsma.kickoff_time DESC
        LIMIT 5
    """)

    def get_recent_form(team_stat_id: str):
        form_rows = db.execute(form_sql, {"team_stat_id": team_stat_id}).fetchall()
        result = []
        for r in form_rows:
            if r.is_home == "t":
                team_score, opp_score = r.home_team_score, r.away_team_score
            else:
                team_score, opp_score = r.away_team_score, r.home_team_score

            if team_score > opp_score:
                result.append("W")
            elif team_score == opp_score:
                result.append("D")
            else:
                result.append("L")
        return result

    grouped = defaultdict(list)
    now_utc = datetime.now(timezone.utc)

    for row in rows:
        kickoff_utc = row.kickoff_time

        if row.period == "FULLTIME":
            status = "finished"
        elif row.period == "PREMATCH" and kickoff_utc <= now_utc <= kickoff_utc + timedelta(minutes=300):
            status = "live"
        else:
            status = "upcoming"

        date_str = kickoff_utc.date().isoformat()

        fixture = {
            "id": row.id,
            "matchweek": row.game_week,
            "kickoff": kickoff_utc.isoformat(),
            "venue": row.name_en if locale == "en-US" else row.name_kr,
            "city": row.city_name_en if locale == "en-US" else row.city_name_kr,
            "status": status,
        }

        if status == "finished" and row.referee_en:
            fixture["referee"] = {
                "main": row.referee_en if locale == "en-US" else row.referee_kr,
                "assist1": None,
                "assist2": None,
                "fourth": None,
            }

        home = {
            "teamId": row.home_team_id,
            "leaguePosition": row.home_position,
            "recentForm": get_recent_form(row.home_team_id),
        }

        away = {
            "teamId": row.away_team_id,
            "leaguePosition": row.away_position,
            "recentForm": get_recent_form(row.away_team_id),
        }

        if status == "finished":
            home["score"] = row.home_team_score
            away["score"] = row.away_team_score

        fixture["home"] = home
        fixture["away"] = away

        grouped[date_str].append(fixture)

    data = [
        {"date": date, "fixtures": fixtures}
        for date, fixtures in grouped.items()
    ]

    KST = timezone(timedelta(hours=9))
    last_updated = datetime.now(KST).strftime("%Y-%m-%dT%H:%M:%S")

    return {
        "data": {
            "dateRange": {
                "startDate": startDate,
                "endDate": endDate,
            },
            "schedule": data,
        },
        "meta": {
            "leagueName": leagueName,
            "leagueId": competition_id,
            "season": season_id,
            "lastUpdated": last_updated,
            "locale": locale,
        }
    }
