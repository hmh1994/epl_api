from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import text 
from database import get_db
from model import dict_to_camel_case

router = APIRouter(prefix="/api/v1/games", tags=["Games"])

@router.get("/")
def overall_teamrank(db : Session = Depends(get_db)):
    query = text("""
                 SELECT 
                    f.id, 
                    ht.name_en AS home_team_name, 
                    at.name_en AS away_team_name, 
                    f.home_team_score, 
                    f.away_team_score, 
                    f.kickoff_time 
                 FROM fixtures f 
                 JOIN teams ht ON f.home_team_id = ht.id 
                 JOIN teams at ON f.away_team_id = at.id
    """)
    result = db.execute(query).fetchall()
    return {"overallGames" : [dict_to_camel_case(row._mapping) for row in result]}

@router.get("/upcoming")
def upcomingGames(db: Session = Depends(get_db)):
    query = text("""
                   SELECT 
    ROW_NUMBER() OVER (ORDER BY f.kickoff_time ASC) AS no,
    f.id,
    ht.name_en AS home_team,
    at.name_en AS away_team,
    f.home_team_id,
    f.away_team_id,
    c.name_en AS league,
    f.kickoff_time,
    ht.icon_url AS home_icon,
    at.icon_url AS away_icon
FROM fixtures f
JOIN teams ht ON f.home_team_id = ht.id
JOIN teams at ON f.away_team_id = at.id
JOIN seasons s ON f.season_id = s.id
JOIN competitions c ON s.competition_id = c.id
WHERE f.season_id = 'PULSELIVE_SEASON_719'
  AND f.kickoff_time > NOW()
ORDER BY f.kickoff_time ASC
LIMIT 10
    """)
    result = db.execute(query).fetchall()
    return {"upcomingGames" : [dict_to_camel_case(row._mapping) for row in result]}

@router.get("/today")
def todayGames(db: Session = Depends(get_db)):
    query = text("""
                    SELECT 
  f.id AS fixture_id,
  th.short_name_en AS home_team,
  ta.short_name_en AS away_team,
  f.kickoff_time,
  f.home_team_score,
  f.away_team_score
FROM fixtures f
JOIN teams th ON f.home_team_id = th.id
JOIN teams ta ON f.away_team_id = ta.id
WHERE f.season_id = 'PULSELIVE_SEASON_719'
  AND DATE(f.kickoff_time) = CURRENT_DATE
ORDER BY f.kickoff_time ASC
LIMIT 5
    """)
    result = db.execute(query).fetchall()
    return {"todayGames" : [dict_to_camel_case(row._mapping) for row in result]}

@router.get("/last")
def lastGames(db: Session = Depends(get_db)):
    query = text("""
SELECT 
  f.id AS fixture_id,
  th.short_name_en AS home_team,
  ta.short_name_en AS away_team,
  f.kickoff_time,
  f.home_team_score,
  f.away_team_score
FROM fixtures f
JOIN teams th ON f.home_team_id = th.id
JOIN teams ta ON f.away_team_id = ta.id
WHERE f.season_id = 'PULSELIVE_SEASON_719'
  AND f.kickoff_time < NOW()
ORDER BY f.kickoff_time DESC
LIMIT 5
    """)
    result = db.execute(query).fetchall()
    return {"lastGames" : [dict_to_camel_case(row._mapping) for row in result]}