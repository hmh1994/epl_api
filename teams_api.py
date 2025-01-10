from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import text 
from database import get_db
from model import dict_to_camel_case
router = APIRouter(prefix="/api/v1/teams", tags=["Teams"])

@router.get("/teamrank")
def overall_teamrank(db : Session = Depends(get_db)):
    query = text("SELECT RANK() OVER (ORDER BY B.overall_points DESC, B.overall_goal_difference DESC) AS ranking, A.short_name_kr, B.overall_matches, B.overall_matches_won, B.overall_matches_drawn, B.overall_matches_lost, B.overall_points, B.overall_goal_difference FROM teams A JOIN standings B ON A.id = B.team_id ORDER BY ranking")
    result = db.execute(query).fetchall()
    return {"overallTeamrank" : [dict_to_camel_case(row._mapping) for row in result]}

