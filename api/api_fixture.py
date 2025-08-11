from collections import defaultdict
from fastapi import APIRouter, Depends
from fastapi import Query
from sqlalchemy.orm import Session
from sqlalchemy.sql import text 
from lib.lib_database import get_db
from lib.lib_camel import dict_to_camel_case, dict_to_camel_case_obj
from datetime import datetime, timedelta
from lib.lib_sql import load_sql
import pytz
import json

router = APIRouter(prefix="/api/v1/match", tags=["Matches"])

@router.get("/")
def all_match_up(db: Session = Depends(get_db)):    
    sql = load_sql("match_list.sql")
    query = text(sql) 
    result = db.execute(query).fetchall()

    kst = pytz.timezone("Asia/Seoul")
    grouped = defaultdict(list)

    for row in result:
        row_dict = row._mapping

        kickoff_time = row_dict["kickoff_time"]
        if isinstance(kickoff_time, str):
            kickoff_time = datetime.fromisoformat(kickoff_time)
        if kickoff_time.tzinfo is None:
            kickoff_time = kickoff_time.replace(tzinfo=pytz.utc)

        date_str = kickoff_time.astimezone(kst).date().isoformat()

        home = {
            "id": row_dict["home_team_id"],
            "nameEn": row_dict["home_team_en"],
            "nameKr": row_dict["home_team_kr"],
            "shortNameEn": row_dict["short_home_team_en"],
            "shortNameKr": row_dict["short_home_team_kr"],
            "iconUrl": row_dict["home_team_img"],
            "score": row_dict["home_team_score"],
        }

        away = {
            "id": row_dict["away_team_id"],
            "nameEn": row_dict["away_team_en"],
            "nameKr": row_dict["away_team_kr"],
            "shortNameEn": row_dict["short_away_team_en"],
            "shortNameKr": row_dict["short_away_team_kr"],
            "iconUrl": row_dict["away_team_img"],
            "score": row_dict["away_team_score"],
        }

        match = {
            "id": row_dict["id"],
            "kickoffTime": kickoff_time.isoformat(),
            "groundEn": row_dict["ground_en"],
            "groundKr": row_dict["ground_kr"],
            "homeTeam": home,
            "awayTeam": away
        }

        grouped[date_str].append(match)

    return dict(grouped)

@router.get("/info/{fixture_id}")
def match_detail(fixture_id: str, db: Session = Depends(get_db)):
    sql = load_sql("match_detail.sql")
    query = text(sql)

    result = db.execute(query, {"fixture_id": fixture_id}).fetchone()

    if not result:
        return {"result": None}

    data = dict(result._mapping)

    for key in [
        "home_lineup", "away_lineup",
        "home_substitutes", "away_substitutes",
        "home_substitutions", "away_substitutions"
    ]:
        val = data.get(key)
        if val and isinstance(val, str):
            try:
                data[key] = json.loads(val)
            except Exception:
                pass

    if data.get("game_stat") and isinstance(data["game_stat"], str):
        try:
            data["game_stat"] = json.loads(data["game_stat"])
        except Exception:
            pass

    home_subs = data.pop("home_substitutions", None)
    away_subs = data.pop("away_substitutions", None)

    if data.get("game_stat"):
        if isinstance(data["game_stat"], dict):
            data["game_stat"]["homeSubstitutions"] = home_subs or []
            data["game_stat"]["awaySubstitutions"] = away_subs or []

    home_keys = [
        "home_lineup", "home_substitutes",
        "home_team_id", "home_team_logo", "home_team_name_en", "short_home_team_name_en",
        "home_team_name_kr", "short_home_team_name_kr",
        "home_team_manager_en", "home_team_manager_kr", "home_team_formation",
        "home_team_recent_form", "home_team_score"
    ]

    away_keys = [
        "away_lineup", "away_substitutes",
        "away_team_id", "away_team_logo", "away_team_name_en", "short_away_team_name_en",
        "away_team_name_kr", "short_away_team_name_kr",
        "away_team_manager_en", "away_team_manager_kr", "away_team_formation",
        "away_team_recent_form", "away_team_score"
    ]

    home_team_info = {}
    away_team_info = {}

    for key in home_keys:
        if key in data:
            home_team_info[key] = data.pop(key)

    for key in away_keys:
        if key in data:
            away_team_info[key] = data.pop(key)

    data["homeTeamInfo"] = home_team_info
    data["awayTeamInfo"] = away_team_info

    return dict_to_camel_case_obj(data)


@router.get("/{timestamp}")
def match_up_by_date(timestamp: int, db: Session = Depends(get_db)):
    kst = pytz.timezone("Asia/Seoul")

    try:
        dt_utc = datetime.utcfromtimestamp(timestamp).replace(tzinfo=pytz.utc)
        dt_kst = dt_utc.astimezone(kst)
    except Exception:
        return {"error": "Invalid timestamp."}

    kst_start = kst.localize(datetime(dt_kst.year, dt_kst.month, dt_kst.day))
    kst_end = kst_start + timedelta(days=1)

    utc_start = kst_start.astimezone(pytz.utc)
    utc_end = kst_end.astimezone(pytz.utc)

    query = text(""" 
    WITH latest_season AS (
        SELECT s.id
        FROM seasons_new s
        JOIN competitions_new c ON s.competition_id = c.id
        WHERE c.abbreviation = 'EN_PR'
        ORDER BY s.date_end DESC
        LIMIT 1
    )
    SELECT 
        fx.id,
        fx.kickoff_time,
        ht.id as home_team_id, 
        ht.name_en as home_team_en,
        ht.name_kr as home_team_kr,
        ht.short_name_en as short_home_team_en,
        ht.short_name_kr as short_home_team_kr,
        ht.icon_url as home_team_img,
        fx.home_team_score,
        at.id as away_team_id, 
        at.name_en as away_team_en,
        at.name_kr as away_team_kr,
        at.short_name_en as short_away_team_en,
        at.short_name_kr as short_away_team_kr,
        at.icon_url as away_team_img,    
        fx.away_team_score,
        gn.name_en as ground_en,
        gn.name_kr as ground_kr	        
    FROM fixtures_new fx
    JOIN teams_new ht ON fx.home_team_id = ht.id
    JOIN teams_new at ON fx.away_team_id = at.id
    JOIN grounds_new gn ON fx.ground_id = gn.id
    WHERE fx.season_id = (SELECT id FROM latest_season)
    AND fx.kickoff_time >= :start_utc
    AND fx.kickoff_time < :end_utc
    ORDER BY fx.kickoff_time DESC
    """)
    result = db.execute(query, {
        "start_utc": utc_start,
        "end_utc": utc_end
    }).fetchall()

    grouped = defaultdict(list)
    date_str = kst_start.date().isoformat() 

    for row in result:
        row_dict = row._mapping

        homeTeam = {
            "id": row_dict["home_team_id"],
            "nameEn": row_dict["home_team_en"],
            "nameKr": row_dict["home_team_kr"],
            "shortNameEn": row_dict["short_home_team_en"],
            "shortNameKr": row_dict["short_home_team_kr"],
            "iconUrl": row_dict["home_team_img"],
            "score": row_dict["home_team_score"],
        }

        awayTeam = {
            "id": row_dict["away_team_id"],
            "nameEn": row_dict["away_team_en"],
            "nameKr": row_dict["away_team_kr"],
            "shortNameEn": row_dict["short_away_team_en"],
            "shortNameKr": row_dict["short_away_team_kr"],
            "iconUrl": row_dict["away_team_img"],
            "score": row_dict["away_team_score"],
        }

        match = {
            "id": row_dict["id"],
            "kickoffTime": row_dict["kickoff_time"].isoformat(),
            "groundEn": row_dict["ground_en"],
            "groundKr": row_dict["ground_kr"],
            "homeTeam": homeTeam,
            "awayTeam": awayTeam
        }

        grouped[date_str].append(match)

    if date_str not in grouped:
        grouped[date_str] = []

    return dict(grouped)

@router.get("/{startdate}/{enddate}")
def match_up_by_range(startdate: int, enddate: int, db: Session = Depends(get_db)):
    try:
        dt_start_utc = datetime.utcfromtimestamp(startdate).replace(tzinfo=pytz.utc)
        dt_end_utc = datetime.utcfromtimestamp(enddate).replace(tzinfo=pytz.utc) + timedelta(days=1)
    except Exception:
        return {"error": "Invalid timestamp."}

    kst = pytz.timezone("Asia/Seoul")
    dt_start_kst = dt_start_utc.astimezone(kst).date()
    dt_end_kst = (dt_end_utc - timedelta(seconds=1)).astimezone(kst).date()

    date_list = []
    current = dt_start_kst
    while current <= dt_end_kst:
        date_list.append(current.isoformat())
        current += timedelta(days=1)

    query = text("""
    WITH latest_season AS (
        SELECT s.id
        FROM seasons_new s
        JOIN competitions_new c ON s.competition_id = c.id
        WHERE c.abbreviation = 'EN_PR'
        ORDER BY s.date_end DESC
        LIMIT 1
    )
    SELECT 
        fx.id,
        fx.kickoff_time,
        ht.id as home_team_id, 
        ht.name_en as home_team_en,
        ht.name_kr as home_team_kr,
        ht.short_name_en as short_home_team_en,
        ht.short_name_kr as short_home_team_kr,
        ht.icon_url as home_team_img,
        fx.home_team_score,
        at.id as away_team_id, 
        at.name_en as away_team_en,
        at.name_kr as away_team_kr,
        at.short_name_en as short_away_team_en,
        at.short_name_kr as short_away_team_kr,
        at.icon_url as away_team_img,    
        fx.away_team_score,
        gn.name_en as ground_en,
        gn.name_kr as ground_kr	     
    FROM fixtures_new fx
    JOIN teams_new ht ON fx.home_team_id = ht.id
    JOIN teams_new at ON fx.away_team_id = at.id
    JOIN grounds_new gn ON fx.ground_id = gn.id
    WHERE fx.season_id = (SELECT id FROM latest_season)
    AND fx.kickoff_time >= :start_utc
    AND fx.kickoff_time < :end_utc
    ORDER BY fx.kickoff_time DESC
    """)

    result = db.execute(query, {
        "start_utc": dt_start_utc,
        "end_utc": dt_end_utc
    }).fetchall()

    grouped = defaultdict(list)

    for row in result:
        row_dict = row._mapping

        kickoff_time = row_dict["kickoff_time"]
        date_str = kickoff_time.astimezone(kst).date().isoformat()

        homeTeam = {
            "id": row_dict["home_team_id"],
            "nameEn": row_dict["home_team_en"],
            "nameKr": row_dict["home_team_kr"],
            "shortNameEn": row_dict["short_home_team_en"],
            "shortNameKr": row_dict["short_home_team_kr"],
            "iconUrl": row_dict["home_team_img"],
            "score": row_dict["home_team_score"],
        }

        awayTeam = {
            "id": row_dict["away_team_id"],
            "nameEn": row_dict["away_team_en"],
            "nameKr": row_dict["away_team_kr"],
            "shortNameEn": row_dict["short_away_team_en"],
            "shortNameKr": row_dict["short_away_team_kr"],
            "iconUrl": row_dict["away_team_img"],
            "score": row_dict["away_team_score"],
        }

        match = {
            "id": row_dict["id"],
            "kickoffTime": kickoff_time.isoformat(),
            "groundEn": row_dict["ground_en"],
            "groundKr": row_dict["ground_kr"],
            "homeTeam": homeTeam,
            "awayTeam": awayTeam
        }

        grouped[date_str].append(match)

    for date in date_list:
        if date not in grouped:
            grouped[date] = []

    return dict(grouped)




'''
@router.get("")
def match_up_by_range_test(
    startdate: int = Query(..., description="Start timestamp"),
    enddate: int = Query(..., description="End timestamp"),
    db: Session = Depends(get_db)
):
    try:
        dt_start_utc = datetime.utcfromtimestamp(startdate).replace(tzinfo=pytz.utc)
        dt_end_utc = datetime.utcfromtimestamp(enddate).replace(tzinfo=pytz.utc)
    except Exception:
        return {"error": "Invalid timestamp."}

    query = text("""
    WITH latest_season AS (
        SELECT s.id
        FROM seasons_new s
        JOIN competitions_new c ON s.competition_id = c.id
        WHERE c.abbreviation = 'EN_PR'
        ORDER BY s.date_end DESC
        LIMIT 1
    )
    SELECT 
        fx.id,
        fx.kickoff_time,
        ht.id as home_team_id, 
        ht.name_en as home_team_en,
        ht.name_kr as home_team_kr,
        ht.short_name_en as short_home_team_en,
        ht.short_name_kr as short_home_team_kr,
        ht.icon_url as home_team_img,
        fx.home_team_score,
        at.id as away_team_id, 
        at.name_en as away_team_en,
        at.name_kr as away_team_kr,
        at.short_name_en as short_away_team_en,
        at.short_name_kr as short_away_team_kr,
        at.icon_url as away_team_img,    
        fx.away_team_score     
    FROM fixtures_new fx
    JOIN teams_new ht ON fx.home_team_id = ht.id
    JOIN teams_new at ON fx.away_team_id = at.id
    WHERE fx.season_id = (SELECT id FROM latest_season)
    AND fx.kickoff_time >= :start_utc
    AND fx.kickoff_time < :end_utc
    ORDER BY fx.kickoff_time DESC
    """)

    result = db.execute(query, {
        "start_utc": dt_start_utc,
        "end_utc": dt_end_utc
    }).fetchall()

    grouped = defaultdict(list)
    for row in result:
        match = dict_to_camel_case(row._mapping)
        kickoff_dt = match["kickoffTime"]
        if isinstance(kickoff_dt, str):
            kickoff_dt = datetime.fromisoformat(kickoff_dt)
        date_str = kickoff_dt.date().isoformat()
        grouped[date_str].append(match)

    return dict(grouped)
    '''