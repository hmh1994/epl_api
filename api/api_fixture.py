from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import text 
from lib.lib_database import get_db
from lib.lib_camel import dict_to_camel_case
from datetime import datetime, timedelta
from lib.lib_sql import load_sql
import pytz

router = APIRouter(prefix="/api/v1/match", tags=["Matches"])

@router.get("/")
def all_match_up(db : Session = Depends(get_db)):    
    sql = load_sql("match_list.sql")
    query = text(sql) 
    result = db.execute(query).fetchall()
    return {"allMatchUp" : [dict_to_camel_case(row._mapping) for row in result]}

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
        "start_utc": utc_start,
        "end_utc": utc_end
    }).fetchall()
    return {"matchUpByDate": [dict_to_camel_case(row._mapping) for row in result]}
