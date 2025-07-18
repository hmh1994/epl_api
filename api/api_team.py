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

'''
@router.get("/rank/detail")
def overall_teamrank_detail(db : Session = Depends(get_db)):
    query = text("""
                            WITH recent_fixtures AS (
                    SELECT 
                        ts.team_id,
                        unnest(ts.overall_fixtures) AS fixture_id
                    FROM team_stats ts
                    WHERE ts.season_id = 'PULSELIVE_SEASON_719'
                ),
                fixture_results AS (
                    SELECT 
                        rf.team_id,
                        f.id AS fixture_id,
                        f.home_team_id,
                        f.away_team_id,
                        f.home_team_score,
                        f.away_team_score,
                        f.kickoff_time,
                        CASE
                            WHEN rf.team_id = f.home_team_id AND f.home_team_score > f.away_team_score THEN 'W'
                            WHEN rf.team_id = f.home_team_id AND f.home_team_score = f.away_team_score THEN 'D'
                            WHEN rf.team_id = f.home_team_id AND f.home_team_score < f.away_team_score THEN 'L'
                            WHEN rf.team_id = f.away_team_id AND f.away_team_score > f.home_team_score THEN 'W'
                            WHEN rf.team_id = f.away_team_id AND f.away_team_score = f.home_team_score THEN 'D'
                            WHEN rf.team_id = f.away_team_id AND f.away_team_score < f.home_team_score THEN 'L'
                        END AS result
                    FROM recent_fixtures rf
                    JOIN fixtures f ON rf.fixture_id = f.id
                ),
                numbered_results AS (
                    SELECT 
                        fr.*,
                        ROW_NUMBER() OVER (PARTITION BY fr.team_id ORDER BY fr.kickoff_time DESC) AS rn
                    FROM fixture_results fr
                    WHERE fr.result IS NOT NULL
                ),
                last_results AS (
                    SELECT 
                        team_id,
                        array_agg(result ORDER BY kickoff_time DESC) AS last_results
                    FROM numbered_results
                    WHERE rn <= 5
                    GROUP BY team_id
                )
                SELECT 
                    RANK() OVER (ORDER BY ts.overall_points DESC) AS rank,
                    ts.team_id,
                    t.name_kr AS team_name,
                    ts.overall_matches,
                    ts.overall_matches_won,
                    ts.overall_matches_drawn,
                    ts.overall_matches_lost,
                    ts.overall_goals_for,
                    ts.overall_goals_against,
                    ts.overall_goals_difference,
                    ts.overall_points,
                    t.icon_url,
                    l5.last_results
                FROM 
                    team_stats ts
                JOIN 
                    teams t ON ts.team_id = t.id
                LEFT JOIN 
                    last_results l5 ON ts.team_id = l5.team_id
                WHERE 
                    ts.season_id = 'PULSELIVE_SEASON_719'
                ORDER BY 
                    ts.overall_points DESC
                 """)
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
    '''