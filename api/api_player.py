from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import text 
from lib.lib_database import get_db
from lib.lib_camel import dict_to_camel_case
from lib.lib_sql import load_sql

router = APIRouter(prefix="/api/v1/player", tags=["Players"])

@router.get("/rank/goal-assist")
def player_rank_goal_assist(db: Session = Depends(get_db)):
    sql = load_sql("player_rank_goal-assist.sql")
    query = text(sql)    
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
	number AS shirt_number,
	ps.player_id,	
	p.display_name_en AS player_name_en,
	p.display_name_kr AS player_name_kr,
	p.full_name AS player_full_name,
	p.photo_url as player_img,
    p.birth_country_en as country_en,
    p.birth_country_kr as country_kr,
	ps.team_id, 
	t.name_en AS team_name_en,
	t.name_kr AS team_name_kr, 
	t.short_name_en AS short_team_name_en,
	t.short_name_kr AS short_team_name_kr,
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
	number AS shirt_number,
	ps.player_id,	
	p.display_name_en AS player_name_en,
	p.display_name_kr AS player_name_kr,
	p.full_name AS player_full_name,
	p.photo_url as player_img,
    p.birth_country_en as country_en,
    p.birth_country_kr as country_kr,
	ps.team_id, 
	t.name_en AS team_name_en,
	t.name_kr AS team_name_kr, 
	t.short_name_en AS short_team_name_en,
	t.short_name_kr AS short_team_name_kr,
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
	number AS shirt_number,
	ps.player_id,	
	p.display_name_en AS player_name_en,
	p.display_name_kr AS player_name_kr,
	p.full_name AS player_full_name,
	p.photo_url as player_img,    
	ps.team_id, 
	t.name_en AS team_name_en,
	t.name_kr AS team_name_kr, 
	t.short_name_en AS short_team_name_en,
	t.short_name_kr AS short_team_name_kr,
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
	number AS shirt_number,
	ps.player_id,	
	p.display_name_en AS player_name_en,
	p.display_name_kr AS player_name_kr,
	p.full_name AS player_full_name,
	p.photo_url as player_img,
    p.birth_country_en as country_en,
    p.birth_country_kr as country_kr,
	ps.team_id, 
	t.name_en AS team_name_en,
	t.name_kr AS team_name_kr, 
	t.short_name_en AS short_team_name_en,
	t.short_name_kr AS short_team_name_kr,
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

@router.get("/{playerId}")
def defender_rank(playerId: str, db: Session = Depends(get_db)):
    query = text("""
	WITH latest_season AS (
		SELECT s.id
		FROM seasons s
		JOIN competitions c ON s.competition_id = c.id
		WHERE c.abbreviation = 'EN_PR'
		ORDER BY s.date_end DESC
		LIMIT 1
	)
	select
	p.id,
	p.display_name_en as player_name_en,
	p.display_name_kr as player_name_kr,
	p.full_name,
	p.position,
	p.position_info_en,
	p.position_info_kr,
	ps.number AS shirt_number,
	p.national_team,
	DATE_PART('year', AGE(NOW(), p.birth_date)) AS age,
	p.birth_date,
	p.birth_country_en,
	p.birth_country_kr,	
	p.height,
	p.weight,
	p.photo_url as playerImg,
	t.name_en as team_en,
	t.name_kr as team_kr,
	t.short_name_en as short_team_en,
	t.short_name_kr as short_team_kr,
	ps.appearances,
	ps.goals,
	ps.assists,
	s.abbreviation	
	from players p
	JOIN player_stats ps ON p.id = ps.player_id 
	JOIN latest_season ls ON ps.season_id = ls.id
	JOIN teams t ON ps.team_id = t.id
	JOIN seasons s ON ls.id = s.id
	WHERE p.id = :player_id
	""")    
    result = db.execute(query, {"player_id": playerId}).fetchone()
    return {
        transform_row(result) 
	}

def transform_row(row):
    data = dict(row._mapping)

    season_fields = [
        "team_en", "team_kr", "short_team_en", "short_team_kr",
        "appearances", "goals", "assists", "abbreviation"
    ]

    season_stats = {field: data.pop(field) for field in season_fields if field in data}

    base = dict_to_camel_case(data)
    season_stats_camel = dict_to_camel_case(season_stats)

    base["seasonStats"] = [season_stats_camel]

    return base