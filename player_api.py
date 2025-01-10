from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import text  
from database import get_db
from model import dict_to_camel_case

router = APIRouter(prefix="/api/v1/player", tags=["Players"])

@router.get("/player_rank")
def player_rank(db : Session = Depends(get_db)):
    query = text("SELECT * from players")
    result = db.execute(query).fetchall()
    return {"playerRank" : [dict_to_camel_case(row._mapping) for row in result]}


'''
WITH goal_ranking AS (
    SELECT 
        RANK() OVER (ORDER BY goals DESC) AS ranking, 
        display_name_kr, 
        team_name, 
        goals AS target
    FROM players
),
assist_ranking AS (
    SELECT 
        RANK() OVER (ORDER BY assists DESC) AS ranking, 
        display_name_kr, 
        team_name, 
        assists AS target
    FROM players
),
yellow_card_ranking AS (
    SELECT 
        RANK() OVER (ORDER BY yellow_cards DESC) AS ranking, 
        display_name_kr, 
        team_name, 
        yellow_cards AS target
    FROM players
),
red_card_ranking AS (
SELECT 
        RANK() OVER (ORDER BY red_cards DESC) AS ranking, 
        display_name_kr, 
        team_name, 
        yellow_cards AS target
    FROM players
)
SELECT 'goal' AS category, * FROM goal_ranking
UNION ALL
SELECT 'assist' AS category, * FROM assist_ranking
UNION ALL
SELECT 'yellowCard' AS category, * FROM yellow_card_ranking;
'''
