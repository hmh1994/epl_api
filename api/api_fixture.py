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
    query = text("""
    WITH base AS (
        SELECT fx.id AS fixture_id, fx.home_team_score, fx.away_team_score, ma.id AS match_id,
               fx.home_team_id, fx.away_team_id
        FROM fixtures_new fx
        JOIN matches_new ma ON fx.id = ma.fixture_id
        WHERE fx.id = :fixture_id
    ),
    static_data AS (
        SELECT
            ms.team_id,
            MAX(ms.possession) AS possession,
            MAX(ms.shots_total) AS shots_total,
            MAX(ms.shots_on_target) AS shots_on_target,
            MAX(ms.fouls_committed) AS fouls_committed,
            MAX(ms.passes_total) AS passes_total,
            MAX(ms.passes_accurate) AS passes_accurate,
            b.home_team_id,
            b.away_team_id
        FROM match_stats_new ms
        JOIN base b ON ms.match_id = b.match_id
        GROUP BY ms.team_id, b.home_team_id, b.away_team_id
    ),
    goals AS (
        SELECT 'home' AS team_side, mhg.clock, p.display_name_en, p.display_name_kr
        FROM match_home_team_goal_association mhg
        JOIN base b ON mhg.match_id = b.match_id
        JOIN players_new p ON mhg.player_id = p.id
        UNION ALL
        SELECT 'away' AS team_side, mag.clock, p.display_name_en, p.display_name_kr
        FROM match_away_team_goal_association mag
        JOIN base b ON mag.match_id = b.match_id
        JOIN players_new p ON mag.player_id = p.id
    ),
    cards AS (
        SELECT 'home' AS team_side, mhc.clock, p.display_name_en, p.display_name_kr, mhc.card_type
        FROM match_home_team_card_association mhc
        JOIN base b ON mhc.match_id = b.match_id
        JOIN players_new p ON mhc.player_id = p.id
        UNION ALL
        SELECT 'away' AS team_side, mac.clock, p.display_name_en, p.display_name_kr, mac.card_type
        FROM match_away_team_card_association mac
        JOIN base b ON mac.match_id = b.match_id
        JOIN players_new p ON mac.player_id = p.id
    )
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
        ht.icon_url AS home_team_logo,
        ht.name_en AS home_team_name_en,
        ht.short_name_en AS short_home_team_name_en,
        ht.name_kr AS home_team_name_kr,
        ht.short_name_kr AS short_home_team_name_kr,
        s1.display_name_en AS home_team_manager_en,
        s1.display_name_kr AS home_team_manager_kr,
        ma.home_team_formation,
        fx.away_team_id,
        at.icon_url AS away_team_logo,
        at.name_en AS away_team_name_en,
        at.short_name_en AS short_away_team_name_en,
        at.name_kr AS away_team_name_kr,
        at.short_name_kr AS short_away_team_name_kr,
        s2.display_name_en AS away_team_manager_en,
        s2.display_name_kr AS away_team_manager_kr,
        ma.away_team_formation,

        htl.home_lineup,
        atl.away_lineup,

        hts.home_substitutes,
        ats.away_substitutes,

        hsubs.home_substitutions,
        asubs.away_substitutions,

        recent_home.home_team_recent_form,
        recent_away.away_team_recent_form,
        b.home_team_score,
        b.away_team_score,
        CASE WHEN b.home_team_score IS NOT NULL AND b.away_team_score IS NOT NULL THEN
            json_build_object(
                'static', json_build_object(
                    'home', json_build_object(
                        'possession', (SELECT possession FROM static_data sd WHERE sd.team_id = b.home_team_id LIMIT 1),
                        'shotsTotal', (SELECT shots_total FROM static_data sd WHERE sd.team_id = b.home_team_id LIMIT 1),
                        'shotsOnTarget', (SELECT shots_on_target FROM static_data sd WHERE sd.team_id = b.home_team_id LIMIT 1),
                        'foulsCommitted', (SELECT fouls_committed FROM static_data sd WHERE sd.team_id = b.home_team_id LIMIT 1),
                        'passesTotal', (SELECT passes_total FROM static_data sd WHERE sd.team_id = b.home_team_id LIMIT 1),
                        'passesAccurate', (SELECT passes_accurate FROM static_data sd WHERE sd.team_id = b.home_team_id LIMIT 1)
                    ),
                    'away', json_build_object(
                        'possession', (SELECT possession FROM static_data sd WHERE sd.team_id = b.away_team_id LIMIT 1),
                        'shotsTotal', (SELECT shots_total FROM static_data sd WHERE sd.team_id = b.away_team_id LIMIT 1),
                        'shotsOnTarget', (SELECT shots_on_target FROM static_data sd WHERE sd.team_id = b.away_team_id LIMIT 1),
                        'foulsCommitted', (SELECT fouls_committed FROM static_data sd WHERE sd.team_id = b.away_team_id LIMIT 1),
                        'passesTotal', (SELECT passes_total FROM static_data sd WHERE sd.team_id = b.away_team_id LIMIT 1),
                        'passesAccurate', (SELECT passes_accurate FROM static_data sd WHERE sd.team_id = b.away_team_id LIMIT 1)
                    )
                ),
                'timeline', json_build_object(
                    'goals', (SELECT json_agg(json_build_object(
                        'teamSide', team_side,
                        'clock', clock,
                        'playerDisplayNameEn', display_name_en,
                        'playerDisplayNameKr', display_name_kr
                    ) ORDER BY clock) FROM goals),
                    'cards', (SELECT json_agg(json_build_object(
                        'teamSide', team_side,
                        'clock', clock,
                        'playerDisplayNameEn', display_name_en,
                        'playerDisplayNameKr', display_name_kr,
                        'cardType', card_type
                    ) ORDER BY clock) FROM cards)
                )
            )
        ELSE NULL END AS game_stat
    FROM fixtures_new fx
    JOIN matches_new ma ON fx.id = ma.fixture_id
    LEFT JOIN teams_new ht ON fx.home_team_id = ht.id
    LEFT JOIN teams_new at ON fx.away_team_id = at.id
    LEFT JOIN staffs_new s1 ON ma.home_team_manager = s1.id
    LEFT JOIN staffs_new s2 ON ma.away_team_manager = s2.id
    LEFT JOIN grounds_new g ON fx.ground_id = g.id
    LEFT JOIN officials_new of ON ma.official_main_referee_id = of.id

    LEFT JOIN LATERAL (
        SELECT JSON_AGG(
            JSON_BUILD_OBJECT(
                'player_id', mht.player_id,
                'shirt_number', mht.shirt_number,
                'row', mht.row,
                'column', mht.column,
                'display_name_en', p.display_name_en,
                'display_name_kr', p.display_name_kr
            ) ORDER BY mht.shirt_number
        ) AS home_lineup
        FROM match_home_team_lineup_association mht
        JOIN players_new p ON p.id = mht.player_id
        WHERE mht.match_id = ma.id
    ) AS htl ON TRUE

    LEFT JOIN LATERAL (
        SELECT JSON_AGG(
            JSON_BUILD_OBJECT(
                'player_id', mat.player_id,
                'shirt_number', mat.shirt_number,
                'row', mat.row,
                'column', mat.column,
                'display_name_en', p.display_name_en,
                'display_name_kr', p.display_name_kr
            ) ORDER BY mat.shirt_number
        ) AS away_lineup
        FROM match_away_team_lineup_association mat
        JOIN players_new p ON p.id = mat.player_id
        WHERE mat.match_id = ma.id
    ) AS atl ON TRUE

    LEFT JOIN LATERAL (
        SELECT JSON_AGG(
            JSON_BUILD_OBJECT(
                'player_id', mhs.player_id,
                'shirt_number', mhs.shirt_number,
                'display_name_en', p.display_name_en,
                'display_name_kr', p.display_name_kr
            ) ORDER BY mhs.shirt_number
        ) AS home_substitutes
        FROM match_home_team_substitute_association mhs
        JOIN players_new p ON p.id = mhs.player_id
        WHERE mhs.match_id = ma.id
    ) AS hts ON TRUE

    LEFT JOIN LATERAL (
        SELECT JSON_AGG(
            JSON_BUILD_OBJECT(
                'player_id', mas.player_id,
                'shirt_number', mas.shirt_number,
                'display_name_en', p.display_name_en,
                'display_name_kr', p.display_name_kr
            ) ORDER BY mas.shirt_number
        ) AS away_substitutes
        FROM match_away_team_substitute_association mas
        JOIN players_new p ON p.id = mas.player_id
        WHERE mas.match_id = ma.id
    ) AS ats ON TRUE

    LEFT JOIN LATERAL (
    SELECT JSON_AGG(
        JSON_BUILD_OBJECT(
            'clock', mhsa.clock,
            'inPlayerDisplayNameEn', pin.display_name_en,
            'inPlayerDisplayNameKr', pin.display_name_kr,
            'inPlayerShirtNumber', COALESCE(mhti.shirt_number, mhti_lineup.shirt_number),
            'outPlayerDisplayNameEn', pout.display_name_en,
            'outPlayerDisplayNameKr', pout.display_name_kr,
            'outPlayerShirtNumber', COALESCE(mhto.shirt_number, mhto_lineup.shirt_number)
        ) ORDER BY mhsa.clock
    ) AS home_substitutions
    FROM match_home_team_substitution_association mhsa
    LEFT JOIN match_home_team_substitute_association mhti 
        ON mhsa.in_player_id = mhti.player_id AND mhsa.match_id = mhti.match_id
    LEFT JOIN match_home_team_lineup_association mhti_lineup
        ON mhsa.in_player_id = mhti_lineup.player_id AND mhsa.match_id = mhti_lineup.match_id
    LEFT JOIN match_home_team_substitute_association mhto 
        ON mhsa.out_player_id = mhto.player_id AND mhsa.match_id = mhto.match_id
    LEFT JOIN match_home_team_lineup_association mhto_lineup
        ON mhsa.out_player_id = mhto_lineup.player_id AND mhsa.match_id = mhto_lineup.match_id
    JOIN players_new pin ON mhsa.in_player_id = pin.id
    JOIN players_new pout ON mhsa.out_player_id = pout.id
) AS hsubs ON TRUE

LEFT JOIN LATERAL (
    SELECT JSON_AGG(
        JSON_BUILD_OBJECT(
            'clock', masa.clock,
            'inPlayerDisplayNameEn', pin.display_name_en,
            'inPlayerDisplayNameKr', pin.display_name_kr,
            'inPlayerShirtNumber', COALESCE(mati.shirt_number, mati_lineup.shirt_number),
            'outPlayerDisplayNameEn', pout.display_name_en,
            'outPlayerDisplayNameKr', pout.display_name_kr,
            'outPlayerShirtNumber', COALESCE(mato.shirt_number, mato_lineup.shirt_number)
        ) ORDER BY masa.clock
    ) AS away_substitutions
    FROM match_away_team_substitution_association masa
    LEFT JOIN match_away_team_substitute_association mati 
        ON masa.in_player_id = mati.player_id AND masa.match_id = mati.match_id
    LEFT JOIN match_away_team_lineup_association mati_lineup
        ON masa.in_player_id = mati_lineup.player_id AND masa.match_id = mati_lineup.match_id
    LEFT JOIN match_away_team_substitute_association mato 
        ON masa.out_player_id = mato.player_id AND masa.match_id = mato.match_id
    LEFT JOIN match_away_team_lineup_association mato_lineup
        ON masa.out_player_id = mato_lineup.player_id AND masa.match_id = mato_lineup.match_id
    JOIN players_new pin ON masa.in_player_id = pin.id
    JOIN players_new pout ON masa.out_player_id = pout.id
) AS asubs ON TRUE

    LEFT JOIN LATERAL (
        SELECT JSON_AGG(result ORDER BY kickoff_time DESC) AS home_team_recent_form
        FROM (
            SELECT CASE 
                    WHEN f.home_team_id = fx.home_team_id THEN 
                        CASE WHEN f.home_team_score > f.away_team_score THEN 'W'
                             WHEN f.home_team_score = f.away_team_score THEN 'D'
                             ELSE 'L'
                        END
                    WHEN f.away_team_id = fx.home_team_id THEN 
                        CASE WHEN f.away_team_score > f.home_team_score THEN 'W'
                             WHEN f.away_team_score = f.home_team_score THEN 'D'
                             ELSE 'L'
                        END
                END AS result,
                f.kickoff_time
            FROM fixtures_new f
            WHERE (f.home_team_id = fx.home_team_id OR f.away_team_id = fx.home_team_id)
              AND f.kickoff_time < fx.kickoff_time
            ORDER BY f.kickoff_time DESC
            LIMIT 5
        ) AS recent
    ) AS recent_home ON TRUE

    LEFT JOIN LATERAL (
        SELECT JSON_AGG(result ORDER BY kickoff_time DESC) AS away_team_recent_form
        FROM (
            SELECT CASE 
                    WHEN f.home_team_id = fx.away_team_id THEN 
                        CASE WHEN f.home_team_score > f.away_team_score THEN 'W'
                             WHEN f.home_team_score = f.away_team_score THEN 'D'
                             ELSE 'L'
                        END
                    WHEN f.away_team_id = fx.away_team_id THEN 
                        CASE WHEN f.away_team_score > f.home_team_score THEN 'W'
                             WHEN f.away_team_score = f.home_team_score THEN 'D'
                             ELSE 'L'
                        END
                END AS result,
                f.kickoff_time
            FROM fixtures_new f
            WHERE (f.home_team_id = fx.away_team_id OR f.away_team_id = fx.away_team_id)
              AND f.kickoff_time < fx.kickoff_time
            ORDER BY f.kickoff_time DESC
            LIMIT 5
        ) AS recent
    ) AS recent_away ON TRUE

    JOIN base b ON b.fixture_id = fx.id
    LEFT JOIN static_data sd ON (sd.team_id = b.home_team_id OR sd.team_id = b.away_team_id)
    LEFT JOIN goals ON true
    LEFT JOIN cards ON true

    WHERE fx.id = :fixture_id;
    """)
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

    # home 관련 키 목록
    home_keys = [
        "home_lineup", "home_substitutes", "home_substitutions",
        "home_team_id", "home_team_logo", "home_team_name_en", "short_home_team_name_en",
        "home_team_name_kr", "short_home_team_name_kr",
        "home_team_manager_en", "home_team_manager_kr", "home_team_formation",
        "home_team_recent_form", "home_team_score"
    ]

    # away 관련 키 목록
    away_keys = [
        "away_lineup", "away_substitutes", "away_substitutions",
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