from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Dict, Any
from lib.lib_database import get_db  
from lib.lib_database import engine

router = APIRouter(prefix="/api/database", tags=["Database"])

def get_table_info():
    inspector = inspect(engine)
    tables = {}
    for table_name in inspector.get_table_names():
        columns = inspector.get_columns(table_name)
        tables[table_name] = columns
    return tables


@router.get("/columns")
def get_columns_only():
    tables = get_table_info()
    return {
        t: [col["name"] for col in cols]
        for t, cols in tables.items()
    }

@router.get("/verify/players/{players_id}")
def verify_players(players_id: str, db: Session = Depends(get_db)) -> dict:
    sql = """
    SELECT *
    FROM players
    WHERE id = :players_id
    """
    query = db.execute(text(sql), {"players_id": players_id})
    row = query.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Player not found")

    return dict(row._mapping)

@router.get("/verify/staffs/{staffs_id}")
def verify_staffs(staffs_id: str, db: Session = Depends(get_db)) -> dict:
    sql = """
    SELECT *
    FROM staffs
    WHERE id = :staffs_id
    """
    query = db.execute(text(sql), {"staffs_id": staffs_id})
    row = query.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Staffs not found")

    return dict(row._mapping)

@router.get("/verify/officials/{officials_id}")
def verify_officials(officials_id: str, db: Session = Depends(get_db)) -> dict:
    sql = """
    SELECT *
    FROM officials
    WHERE id = :officials_id
    """
    query = db.execute(text(sql), {"officials_id": officials_id})
    row = query.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Officials not found")

    return dict(row._mapping)

@router.get("/verify/competitions/{competitions_id}")
def verify_competitions(competitions_id: str, db: Session = Depends(get_db)) -> dict:
    sql = """
    SELECT *
    FROM competitions
    WHERE id = :competitions_id
    """
    query = db.execute(text(sql), {"competitions_id": competitions_id})
    row = query.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Competitions not found")

    return dict(row._mapping)

@router.get("/verify/news/{news_id}")
def verify_news(news_id: str, db: Session = Depends(get_db)) -> dict:
    sql = """
    SELECT *
    FROM news
    WHERE id = :news_id
    """
    query = db.execute(text(sql), {"news_id": news_id})
    row = query.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="News not found")

    return dict(row._mapping)

@router.get("/verify/teams/{teams_id}")
def verify_teams(teams_id: str, db: Session = Depends(get_db)) -> dict:
    sql = """
    SELECT *
    FROM teams
    WHERE id = :teams_id
    """
    query = db.execute(text(sql), {"teams_id": teams_id})
    row = query.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Teams not found")

    return dict(row._mapping)

@router.get("/verify/grounds/{grounds_id}")
def verify_grounds(grounds_id: str, db: Session = Depends(get_db)) -> dict:
    sql = """
    SELECT *
    FROM grounds
    WHERE id = :grounds_id
    """
    query = db.execute(text(sql), {"grounds_id": grounds_id})
    row = query.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Grounds not found")

    return dict(row._mapping)

@router.get("/verify/awards/{awards_id}")
def verify_awards(awards_id: str, db: Session = Depends(get_db)) -> dict:
    sql = """
    SELECT *
    FROM awards
    WHERE id = :awards_id
    """
    query = db.execute(text(sql), {"awards_id": awards_id})
    row = query.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Awards not found")

    return dict(row._mapping)


@router.get("/verify/match_stats/{match_stats_id}")
def verify_match_stats(match_stats_id: str, db: Session = Depends(get_db)) -> dict:
    sql = """
    SELECT 
        ms.*,
        (
            SELECT json_agg(m.*)
            FROM matches m
            WHERE m.id = ms.match_id
        ) AS matches,
        (
            SELECT json_agg(t.*)
            FROM teams t
            WHERE t.id = ms.team_id
        ) AS teams
    FROM match_stats ms
    WHERE id = :match_stats_id
    """
    query = db.execute(text(sql), {"match_stats_id": match_stats_id})
    row = query.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Match_stats not found")

    return dict(row._mapping)


@router.get("/verify/team_stats/{team_stats_id}")
def verify_match_stats(team_stats_id: str, db: Session = Depends(get_db)) -> dict:
    sql = """
    SELECT 
        ms.*,
        (
            SELECT json_agg(m.*)
            FROM grounds m
            WHERE m.id = ms.ground_id
        ) AS grounds,
        (select json_agg(a.*) from staffs a where a.id = ms.manager_id) AS managers,
        (select json_agg(b.*) from seasons b where b.id = ms.season_id) AS season,
        (select json_agg(c.*) from teams c where c.id = ms.team_id) AS team,
    FROM team_stats ms
    WHERE id = :team_stats_id
    """
    query = db.execute(text(sql), {"team_stats_id": team_stats_id})
    row = query.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="team_stats not found")

    return dict(row._mapping)