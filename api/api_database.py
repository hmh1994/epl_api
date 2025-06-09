from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from lib.lib_database import get_db

router = APIRouter(prefix="/api/database", tags=["Database"])

@router.get("/competitions")
def get_competitions(db: Session = Depends(get_db)):
    query = text("SELECT * FROM competitions")
    result = db.execute(query).fetchall()
    return {"competitions": [dict(row._mapping) for row in result]}

@router.get("/fixtures")
def get_fixtures(db: Session = Depends(get_db)):
    query = text("SELECT * FROM fixtures")
    result = db.execute(query).fetchall()
    return {"fixtures": [dict(row._mapping) for row in result]}

@router.get("/grounds")
def get_grounds(db: Session = Depends(get_db)):
    query = text("SELECT * FROM grounds")
    result = db.execute(query).fetchall()
    return {"grounds": [dict(row._mapping) for row in result]}

@router.get("/metadata")
def get_metadata(db: Session = Depends(get_db)):
    query = text("SELECT * FROM metadata")
    result = db.execute(query).fetchall()
    return {"metadata": [dict(row._mapping) for row in result]}

@router.get("/news")
def get_news(db: Session = Depends(get_db)):
    query = text("SELECT * FROM news")
    result = db.execute(query).fetchall()
    return {"news": [dict(row._mapping) for row in result]}

@router.get("/playerStats")
def get_playerStats(db: Session = Depends(get_db)):
    query = text("SELECT * FROM player_stats")
    result = db.execute(query).fetchall()
    return {"playerStats": [dict(row._mapping) for row in result]}

@router.get("/players")
def get_players(db: Session = Depends(get_db)):
    query = text("SELECT * FROM players")
    result = db.execute(query).fetchall()
    return {"players": [dict(row._mapping) for row in result]}

@router.get("/seasons")
def get_seasons(db: Session = Depends(get_db)):
    query = text("SELECT * FROM seasons")
    result = db.execute(query).fetchall()
    return {"seasons": [dict(row._mapping) for row in result]}

@router.get("/teamStats")
def get_teamStats(db: Session = Depends(get_db)):
    query = text("SELECT * FROM team_stats")
    result = db.execute(query).fetchall()
    return {"teamStats": [dict(row._mapping) for row in result]}


@router.get("/teams")
def get_teams(db: Session = Depends(get_db)):
    query = text("SELECT * FROM teams")
    result = db.execute(query).fetchall()
    return {"teams": [dict(row._mapping) for row in result]}
