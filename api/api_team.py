from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import text 
from lib.lib_database import get_db
from lib.lib_camel import dict_to_camel_case
from lib.lib_sql import load_sql

router = APIRouter(prefix="/api/v1/teams", tags=["Teams"])

@router.get("/rank")
def teamrank(db : Session = Depends(get_db)):
    sql = load_sql("team_rank.sql")
    query = text(sql)   
    result = db.execute(query).fetchall()
    return {"Teamrank" : [dict_to_camel_case(row._mapping) for row in result]}


@router.get("/rank/detail")
def teamrank_detail(db : Session = Depends(get_db)):
    sql = load_sql("team_rank_detail.sql")
    query = text(sql)   
    result = db.execute(query).fetchall()
    return {"overallTeamrankDetail" : [dict(row._mapping) for row in result]}

@router.get("/rank/score")
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
    return {"topScoreTeam" : [dict(row._mapping) for row in result]}


@router.get("/rank/defend")
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
    return {"topDefendTeam" : [dict(row._mapping) for row in result]}

@router.get("/rank/point")
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
    return {"topPointTeam" : [dict(row._mapping) for row in result]}
    