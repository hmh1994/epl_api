from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import text 
from database import get_db
from model import dict_to_camel_case

router = APIRouter(prefix="/api/v1/games", tags=["Games"])

@router.get("/allgames")
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

@router.get("/seasons")
def get_seasons_by_competition(competition_id: str, db: Session = Depends(get_db)):
    query = text("""
        SELECT 
            s.id, 
            s.abbreviation, 
            s.date_end, 
            s.date_start, 
            s.year_end, 
            s.year_start, 
            c.name_en AS competition_name_en
        FROM seasons s
        JOIN competitions c ON s.competition_id = c.id
        WHERE s.competition_id = :competition_id
        ORDER BY date_end DESC
    """)
    result = db.execute(query, {"competition_id": competition_id}).fetchall()
    return {"seasons": [dict_to_camel_case(row._mapping) for row in result]}
