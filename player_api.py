from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import text  
from database import get_db
from model import dict_to_camel_case

router = APIRouter(prefix="/api/v1/player", tags=["Players"])

@router.get("/playerAssistRank")
def player_assist_rank(db : Session = Depends(get_db)):
    query = text("""
                SELECT 
                RANK() OVER (ORDER BY ps.assists DESC) AS rank,
                ps.player_id,
                ps.assists,
                p.display_name_en
                FROM player_stats ps
                JOIN players p ON ps.player_id = p.id
                WHERE ps.season_id = 'PULSELIVE_SEASON_719'
                ORDER BY ps.assists DESC
                LIMIT 10
                 """)
    result = db.execute(query).fetchall()
    return {"playerAssistRank" : [dict_to_camel_case(row._mapping) for row in result]}



@router.get("/playerGoalRank")
def player_goal_rank(db : Session = Depends(get_db)):
    query = text("""
                SELECT 
                RANK() OVER (ORDER BY ps.goals DESC) AS rank,
                ps.player_id,
                ps.goals,
                p.display_name_en
                FROM player_stats ps
                JOIN players p ON ps.player_id = p.id
                WHERE ps.season_id = 'PULSELIVE_SEASON_719'
                ORDER BY ps.goals DESC
                LIMIT 10
                 """)
    result = db.execute(query).fetchall()
    return {"playerGoalRank" : [dict_to_camel_case(row._mapping) for row in result]}