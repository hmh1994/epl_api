from collections import defaultdict
from fastapi import APIRouter, Depends
from fastapi import Query
from sqlalchemy.orm import Session
from sqlalchemy.sql import text 
from lib.lib_database import get_db
from lib.lib_camel import dict_to_camel_case
from datetime import datetime, timedelta
from lib.lib_sql import load_sql
import pytz

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

@router.get("/infotest")
def match_detail(db: Session = Depends(get_db)):
    query = text("""
    SELECT 
        fx.id, 
        g.name_en AS ground_name_en,
        g.name_kr AS ground_name_kr,
        g.city_name_en,
        g.city_name_kr,
        g.capacity,
        fx.kickoff_time,
        of.display_name_en AS official_name_en,
        of.display_name_kr AS official_name_kr,
        fx.home_team_id,
        s1.display_name_en AS home_team_manager_en,
        s1.display_name_kr AS home_team_manager_kr,
        ma.home_team_formation,
        fx.away_team_id,
        s2.display_name_en AS away_team_manager_en,
        s2.display_name_kr AS away_team_manager_kr,
        ma.away_team_formation,
        htl.home_lineup,
        atl.away_lineup,
        hts.home_substitutes,
        ats.away_substitutes
    FROM fixtures_new fx
    JOIN matches_new ma ON fx.id = ma.fixture_id
    LEFT JOIN staffs_new s1 ON ma.home_team_manager = s1.id
    LEFT JOIN staffs_new s2 ON ma.away_team_manager = s2.id
    LEFT JOIN grounds_new g ON fx.ground_id = g.id
    LEFT JOIN officials_new of ON ma.official_main_referee_id = of.id

    -- 홈 선발 라인업
    LEFT JOIN LATERAL (
        SELECT JSON_AGG(
            JSON_BUILD_OBJECT(
                'player_id', mht.player_id,
                'shirt_number', mht.shirt_number,
                'row', mht.row,
                'column', mht.column
            ) ORDER BY mht.shirt_number
        ) AS home_lineup
        FROM match_home_team_lineup_association mht
        WHERE mht.match_id = ma.id
    ) AS htl ON TRUE

    -- 어웨이 선발 라인업
    LEFT JOIN LATERAL (
        SELECT JSON_AGG(
            JSON_BUILD_OBJECT(
                'player_id', mat.player_id,
                'shirt_number', mat.shirt_number,
                'row', mat.row,
                'column', mat.column
            ) ORDER BY mat.shirt_number
        ) AS away_lineup
        FROM match_away_team_lineup_association mat
        WHERE mat.match_id = ma.id
    ) AS atl ON TRUE

    -- 홈 후보 선수
    LEFT JOIN LATERAL (
        SELECT JSON_AGG(
            JSON_BUILD_OBJECT(
                'player_id', mhs.player_id,
                'shirt_number', mhs.shirt_number
            ) ORDER BY mhs.shirt_number
        ) AS home_substitutes
        FROM match_home_team_substitute_association mhs
        WHERE mhs.match_id = ma.id
    ) AS hts ON TRUE

    -- 어웨이 후보 선수
    LEFT JOIN LATERAL (
        SELECT JSON_AGG(
            JSON_BUILD_OBJECT(
                'player_id', mas.player_id,
                'shirt_number', mas.shirt_number
            ) ORDER BY mas.shirt_number
        ) AS away_substitutes
        FROM match_away_team_substitute_association mas
        WHERE mas.match_id = ma.id
    ) AS ats ON TRUE

    WHERE fx.id = '33e09323-9d46-45e1-a734-1b2bb968afb3';
    """)

    result = db.execute(query).fetchone()

    if not result:
        return {"result": None}
    
    return {
        "result": dict_to_camel_case(result._mapping)
    }

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