from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import text 
from lib.lib_database import get_db
from lib.lib_camel import dict_to_camel_case

router = APIRouter(prefix="/api/v1/match", tags=["Matches"])

@router.get("/")
def all_match_up(db : Session = Depends(get_db)):
    '''
    query = text("""
WITH latest_season AS (
    SELECT s.id
    FROM seasons s
    JOIN competitions c ON s.competition_id = c.id
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
	
FROM fixtures fx
JOIN teams ht ON fx.home_team_id = ht.id
JOIN teams at ON fx.away_team_id = at.id
WHERE fx.season_id = (SELECT id FROM latest_season)
ORDER BY fx.kickoff_time DESC
    """)
    '''
    query = text("""
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
	
FROM fixtures fx
JOIN teams ht ON fx.home_team_id = ht.id
JOIN teams at ON fx.away_team_id = at.id
WHERE fx.season_id = 'b6a1c699-49da-45b9-9edc-b24d80eb9156'
ORDER BY fx.kickoff_time DESC
                 """)
    result = db.execute(query).fetchall()
    return {"allMatchUp" : [dict_to_camel_case(row._mapping) for row in result]}

@router.get("/{date}")
def match_up_by_date(date: str, db: Session = Depends(get_db)):
    query = text(""" 
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
        FROM fixtures fx
        JOIN teams ht ON fx.home_team_id = ht.id
        JOIN teams at ON fx.away_team_id = at.id
        WHERE fx.season_id = 'b6a1c699-49da-45b9-9edc-b24d80eb9156'
        AND DATE(fx.kickoff_time) = :date
        ORDER BY fx.kickoff_time DESC
    """)
    result = db.execute(query, {"date": date}).fetchall()
    return {"matchUpByDate": [dict_to_camel_case(row._mapping) for row in result]}