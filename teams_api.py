from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import text 
from database import get_db
from model import dict_to_camel_case
router = APIRouter(prefix="/api/v1/teams", tags=["Teams"])

@router.get("/teamrank")
def overall_teamrank(db : Session = Depends(get_db)):
    query = text("""
               SELECT 
                    RANK() OVER (ORDER BY ts.overall_points DESC) AS rank,
                    t.short_name_en,
                    ts.team_id,
                    ts.overall_matches,
                    ts.overall_matches_won,
                    ts.overall_matches_drawn,
                    ts.overall_matches_lost,
                    ts.overall_goals_difference,
                    ts.overall_points,
                    t.icon_url
                FROM team_stats ts
                JOIN teams t ON ts.team_id = t.id
                WHERE ts.season_id = 'PULSELIVE_SEASON_719'
                ORDER BY ts.overall_points DESC
                 """)
    result = db.execute(query).fetchall()
    return {"overallTeamrank" : [dict_to_camel_case(row._mapping) for row in result]}

@router.get("/top_score_team")
def top_score_team(db : Session = Depends(get_db)):
    query = text("""
                SELECT
                    RANK() OVER (ORDER BY ts.overall_goals_for DESC) AS rank,
                    t.name_en AS team_name,
                    c.name_en AS league_name,
                    ts.overall_goals_for
                FROM team_stats ts
                JOIN teams t ON ts.team_id = t.id
                JOIN seasons s ON ts.season_id = s.id
                JOIN competitions c ON s.competition_id = c.id
                ORDER BY ts.overall_goals_for DESC
                LIMIT 5
    """)
    result = db.execute(query).fetchall()
    return {"topScoreTeam" : [dict_to_camel_case(row._mapping) for row in result]}


@router.get("/top_defend_team")
def top_defend_team(db : Session = Depends(get_db)):
    query = text("""
                SELECT
                    RANK() OVER (ORDER BY ts.overall_goals_against ASC) AS rank,
                    t.name_en AS team_name,
                    c.name_en AS league_name,
                    ts.overall_goals_against
                FROM team_stats ts
                JOIN teams t ON ts.team_id = t.id
                JOIN seasons s ON ts.season_id = s.id
                JOIN competitions c ON s.competition_id = c.id
                ORDER BY ts.overall_goals_against ASC
                LIMIT 5
    """)
    result = db.execute(query).fetchall()
    return {"topDefendTeam" : [dict_to_camel_case(row._mapping) for row in result]}

@router.get("/top_points_team")
def top_points_team(db : Session = Depends(get_db)):
    query = text("""
                SELECT
                    RANK() OVER (ORDER BY ts.overall_points DESC) AS rank,
                    t.name_en AS team_name,
                    c.name_en AS league_name,
                    ts.overall_points
                FROM team_stats ts
                JOIN teams t ON ts.team_id = t.id
                JOIN seasons s ON ts.season_id = s.id
                JOIN competitions c ON s.competition_id = c.id
                ORDER BY ts.overall_points DESC
                LIMIT 5
    """)
    result = db.execute(query).fetchall()
    return {"topPointTeam" : [dict_to_camel_case(row._mapping) for row in result]}