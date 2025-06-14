from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import text 
from lib.lib_database import get_db
from lib.lib_camel import dict_to_camel_case

router = APIRouter(prefix="/api/v1/player", tags=["Players"])

@router.get("/rank/goal-assist")
def player_rank_goal_assist(db: Session = Depends(get_db)):
    query = text("""
WITH latest_season AS (
    SELECT s.id
    FROM seasons s
    JOIN competitions c ON s.competition_id = c.id
    WHERE c.abbreviation = 'EN_PR'
    ORDER BY s.date_end DESC
    LIMIT 1
)
SELECT * FROM (
SELECT 
	RANK() OVER (ORDER BY ps.goals DESC) AS rank,
	number,
	ps.player_id,	
	p.display_name_en AS player_name_en,
	p.display_name_kr AS player_name_kr,
	p.full_name AS player_full_name,
	p.photo_url as player_img,
    p.birth_country_en as countryEn,
    p.birth_country_kr as countryKr,
	ps.team_id, 
	t.name_en AS team_name_en,
	t.name_kr AS team_name_kr, 
	t.short_name_en AS steam_name_en,
	t.short_name_kr AS steam_name_kr,
	t.icon_url AS team_icon,
	ps.appearances,
	ps.goals,
    ps.assists,
	DATE_PART('year', AGE(NOW(), p.birth_date)) AS age,
    'goal' AS category
FROM player_stats ps
JOIN players p ON ps.player_id = p.id
JOIN teams t ON ps.team_id = t.id
WHERE ps.season_id = (SELECT id FROM latest_season)
LIMIT 5) as goal_ranks

UNION ALL
select * from (
SELECT 
	RANK() OVER (ORDER BY ps.assists DESC) AS rank,
	number,
	ps.player_id,	
	p.display_name_en AS player_name_en,
	p.display_name_kr AS player_name_kr,
	p.full_name AS player_full_name,
	p.photo_url as player_img,
    p.birth_country_en as countryEn,
    p.birth_country_kr as countryKr,
	ps.team_id, 
	t.name_en AS team_name_en,
	t.name_kr AS team_name_kr, 
	t.short_name_en AS steam_name_en,
	t.short_name_kr AS steam_name_kr,
	t.icon_url AS team_icon,
	ps.appearances,
    ps.goals,
	ps.assists,
	DATE_PART('year', AGE(NOW(), p.birth_date)) AS age,
    'assist' AS category
FROM player_stats ps
JOIN players p ON ps.player_id = p.id
JOIN teams t ON ps.team_id = t.id
WHERE ps.season_id = (SELECT id FROM latest_season)
LIMIT 5
) as assist_ranks
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
WITH latest_season AS (
    SELECT s.id
    FROM seasons s
    JOIN competitions c ON s.competition_id = c.id
    WHERE c.abbreviation = 'EN_PR'
    ORDER BY s.date_end DESC
    LIMIT 1
)
SELECT 
	RANK() OVER (ORDER BY ps.goals DESC) AS rank,
	number,
	ps.player_id,	
	p.display_name_en AS player_name_en,
	p.display_name_kr AS player_name_kr,
	p.full_name AS player_full_name,
	p.photo_url as player_img,
    p.birth_country_en as countryEn,
    p.birth_country_kr as countryKr,
	ps.team_id, 
	t.name_en AS team_name_en,
	t.name_kr AS team_name_kr, 
	t.short_name_en AS steam_name_en,
	t.short_name_kr AS steam_name_kr,
	t.icon_url AS team_icon,
	ps.appearances,
	ps.goals,
    ps.assists,
	DATE_PART('year', AGE(NOW(), p.birth_date)) AS age
FROM player_stats ps
JOIN players p ON ps.player_id = p.id
JOIN teams t ON ps.team_id = t.id
WHERE ps.season_id = (SELECT id FROM latest_season)
LIMIT 10
    """)

    result = db.execute(query).fetchall()
    return {
        "playerGoalRank": [dict_to_camel_case(row._mapping) for row in result]
    }

@router.get("/rank/assist")
def player_assist_rank(db: Session = Depends(get_db)):
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
	RANK() OVER (ORDER BY ps.assists DESC) AS rank,
	number,
	ps.player_id,	
	p.display_name_en AS player_name_en,
	p.display_name_kr AS player_name_kr,
	p.full_name AS player_full_name,
	p.photo_url as player_img,
    p.birth_country_en as countryEn,
    p.birth_country_kr as countryKr,
	ps.team_id, 
	t.name_en AS team_name_en,
	t.name_kr AS team_name_kr, 
	t.short_name_en AS steam_name_en,
	t.short_name_kr AS steam_name_kr,
	t.icon_url AS team_icon,
	ps.appearances,
	ps.goals,
    ps.assists,
	DATE_PART('year', AGE(NOW(), p.birth_date)) AS age
FROM player_stats ps
JOIN players p ON ps.player_id = p.id
JOIN teams t ON ps.team_id = t.id
WHERE ps.season_id = (SELECT id FROM latest_season)
LIMIT 10
    """)
    result = db.execute(query).fetchall()
    return {
        "playerAssistRank": [dict_to_camel_case(row._mapping) for row in result]
    }

@router.get("/rank/goal-keep")
def goalkeeper_rank(db: Session = Depends(get_db)):
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
	RANK() OVER (ORDER BY ps.saves DESC) AS rank,
	number,
	ps.player_id,	
	p.display_name_en AS player_name_en,
	p.display_name_kr AS player_name_kr,
	p.full_name AS player_full_name,
	p.photo_url as player_img,
    
	ps.team_id, 
	t.name_en AS team_name_en,
	t.name_kr AS team_name_kr, 
	t.short_name_en AS steam_name_en,
	t.short_name_kr AS steam_name_kr,
	t.icon_url AS team_icon,
	ps.appearances,
	ps.saves,
	DATE_PART('year', AGE(NOW(), p.birth_date)) AS age
FROM player_stats ps
JOIN players p ON ps.player_id = p.id
JOIN teams t ON ps.team_id = t.id
WHERE ps.season_id = (SELECT id FROM latest_season)
LIMIT 10
    """)
    result = db.execute(query).fetchall()
    return {
        "playerGoalKeepRank": [dict_to_camel_case(row._mapping) for row in result]
    }

@router.get("/rank/defend")
def defender_rank(db: Session = Depends(get_db)):
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
	RANK() OVER (ORDER BY ps.clean_sheets DESC) AS rank,
	number,
	ps.player_id,	
	p.display_name_en AS player_name_en,
	p.display_name_kr AS player_name_kr,
	p.full_name AS player_full_name,
	p.photo_url as player_img,
    p.birth_country_en as countryEn,
    p.birth_country_kr as countryKr,
	ps.team_id, 
	t.name_en AS team_name_en,
	t.name_kr AS team_name_kr, 
	t.short_name_en AS steam_name_en,
	t.short_name_kr AS steam_name_kr,
	t.icon_url AS team_icon,
	ps.appearances,
	ps.clean_sheets,
	DATE_PART('year', AGE(NOW(), p.birth_date)) AS age
FROM player_stats ps
JOIN players p ON ps.player_id = p.id
JOIN teams t ON ps.team_id = t.id
WHERE ps.season_id = (SELECT id FROM latest_season)
LIMIT 10
    """)
    result = db.execute(query).fetchall()
    return {
        "playerDefendRank": [dict_to_camel_case(row._mapping) for row in result]
    }