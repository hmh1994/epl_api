from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.sql import text  
from database import get_db
from model import dict_to_camel_case

router = APIRouter(prefix="/api/v1/player", tags=["Players"])

@router.get("/rank/goal-assist")
def player_rank_goal_assist(db: Session = Depends(get_db)):
    query = text("""
        SELECT * FROM (
            SELECT
                ROW_NUMBER() OVER (ORDER BY ps.goals DESC) AS rank,
                p.full_name AS player_name,
                ps.player_id,
                k.name_en AS team_name,
                k.id AS team_id,
                ps.goals AS stat_value,
                p.photo_url,
                k.icon_url,
                'goal' AS category
            FROM player_stats ps
            JOIN players p ON ps.player_id = p.id
            JOIN teams k ON ps.team_id = k.id
            WHERE ps.season_id = 'PULSELIVE_SEASON_719'
            AND ps.goals > 0
            ORDER BY ps.goals DESC
            LIMIT 20
        ) AS goal_rankings

        UNION ALL

        SELECT * FROM (
            SELECT
                ROW_NUMBER() OVER (ORDER BY ps.assists DESC) AS rank,
                p.full_name AS player_name,
                ps.player_id,
                k.name_en AS team_name,
                k.id AS team_id,
                ps.assists AS stat_value,
                p.photo_url,
                k.icon_url,
                'assist' AS category
            FROM player_stats ps
            JOIN players p ON ps.player_id = p.id
            JOIN teams k ON ps.team_id = k.id
            WHERE ps.season_id = 'PULSELIVE_SEASON_719'
            AND ps.assists > 0
            ORDER BY ps.assists DESC
            LIMIT 20
        ) AS assist_rankings
    """)

    result = db.execute(query).fetchall()

    goal_ranks = []
    assist_ranks = []
    for row in result:
        row_dict = dict_to_camel_case(row._mapping)
        if row_dict["category"] == "goal":
            goal_ranks.append(row_dict)
        elif row_dict["category"] == "assist":
            assist_ranks.append(row_dict)

    return {
        "goalRanks": goal_ranks,
        "assistRanks": assist_ranks
    }
@router.get("/rank/goal")
def player_goal_rank(db: Session = Depends(get_db)):
    query = text("""
        SELECT 
            RANK() OVER (ORDER BY ps.goals DESC) AS rank,
            ps.number,
            p.display_name_en AS player,
            p.id AS player_id,
            t.name_en AS team,
            t.id AS team_id,
            c.name_en AS league,
            p.birth_country_en AS nationality,
            DATE_PART('year', AGE(NOW(), p.birth_date)) AS age,
            ps.goals,
            ps.assists,
            ps.appearances,
            ROUND(CASE 
                WHEN ps.appearances = 0 THEN 0
                ELSE ps.goals::decimal / ps.appearances 
            END, 2) AS goals_per_match,
            p.photo_url AS avatar,
            t.icon_url AS team_logo
        FROM player_stats ps
        JOIN players p ON ps.player_id = p.id
        JOIN teams t ON ps.team_id = t.id
        JOIN seasons s ON ps.season_id = s.id
        JOIN competitions c ON s.competition_id = c.id
        WHERE ps.season_id = 'PULSELIVE_SEASON_719'
        AND s.competition_id = 'PULSELIVE_COMPETITION_1'
        ORDER BY ps.goals DESC, ps.appearances ASC
        LIMIT 10
    """)

    result = db.execute(query).fetchall()
    return {
        "playerGoalRank": [dict_to_camel_case(row._mapping) for row in result]
    }

@router.get("/rank/assist")
def player_assist_rank(db: Session = Depends(get_db)):
    query = text("""
        SELECT 
            RANK() OVER (ORDER BY ps.assists DESC) AS rank,
            p.display_name_en AS player,
            p.id AS player_id,
            t.name_en AS team,
            t.id AS team_id,
            c.name_en AS league,
            p.birth_country_en AS nationality,
            DATE_PART('year', AGE(NOW(), p.birth_date)) AS age,
            ps.goals,
            ps.assists,
            ps.appearances,
            ROUND(CASE 
                WHEN ps.appearances = 0 THEN 0
                ELSE ps.assists::decimal / ps.appearances 
            END, 2) AS assists_per_match,
            p.photo_url AS avatar,
            t.icon_url AS team_logo
        FROM player_stats ps
        JOIN players p ON ps.player_id = p.id
        JOIN teams t ON ps.team_id = t.id
        JOIN seasons s ON ps.season_id = s.id
        JOIN competitions c ON s.competition_id = c.id
        WHERE ps.season_id = 'PULSELIVE_SEASON_719'
        AND s.competition_id = 'PULSELIVE_COMPETITION_1'
        ORDER BY ps.assists DESC, ps.appearances ASC
        LIMIT 10
    """)
    result = db.execute(query).fetchall()
    return {
        "playerAssistRank": [dict_to_camel_case(row._mapping) for row in result]
    }

@router.get("/rank/goal-keep")
def goalkeeper_rank(db: Session = Depends(get_db)):
    query = text("""
        SELECT 
            RANK() OVER (ORDER BY ps.clean_sheets DESC) AS rank,
            p.display_name_en AS player,
            p.id AS player_id,
            t.name_en AS team,
            t.id AS team_id,
            c.name_en AS league,
            p.birth_country_en AS nationality,
            DATE_PART('year', AGE(NOW(), p.birth_date)) AS age,
            ps.clean_sheets,
            ps.appearances,
            ps.goals_conceded,
            ps.saves,
            p.photo_url AS avatar,
            t.icon_url AS team_logo
        FROM player_stats ps
        JOIN players p ON ps.player_id = p.id
        JOIN teams t ON ps.team_id = t.id
        JOIN seasons s ON ps.season_id = s.id
        JOIN competitions c ON s.competition_id = c.id
        WHERE ps.season_id = 'PULSELIVE_SEASON_719'
        AND s.competition_id = 'PULSELIVE_COMPETITION_1'
        AND p.position = 'G'
        ORDER BY ps.clean_sheets DESC, ps.goals_conceded ASC
        LIMIT 10
    """)
    result = db.execute(query).fetchall()
    return {
        "goalkeeperRank": [dict_to_camel_case(row._mapping) for row in result]
    }

@router.get("/rank/defend")
def defender_rank(db: Session = Depends(get_db)):
    query = text("""
        SELECT 
            RANK() OVER (ORDER BY ps.clean_sheets DESC) AS rank,
            p.display_name_en AS player,
            p.id AS player_id,
            t.name_en AS team,
            t.id AS team_id,
            c.name_en AS league,
            p.birth_country_en AS nationality,
            DATE_PART('year', AGE(NOW(), p.birth_date)) AS age,
            ps.appearances,
            ps.goals,
            ps.assists,
            ps.clean_sheets,
            ps.tackles,
            p.photo_url AS avatar,
            t.icon_url AS team_logo
        FROM player_stats ps
        JOIN players p ON ps.player_id = p.id
        JOIN teams t ON ps.team_id = t.id
        JOIN seasons s ON ps.season_id = s.id
        JOIN competitions c ON s.competition_id = c.id
        WHERE ps.season_id = 'PULSELIVE_SEASON_719'
        AND s.competition_id = 'PULSELIVE_COMPETITION_1'
        AND p.position IN ('D')  -- 수비수
        ORDER BY ps.clean_sheets DESC, ps.appearances DESC
        LIMIT 10
    """)
    result = db.execute(query).fetchall()
    return {
        "defenderRank": [dict_to_camel_case(row._mapping) for row in result]
    }