from fastapi import FastAPI, HTTPException
#from sqlalchemy.orm import Session
#from sqlalchemy import text
#from database import SessionLocal
from sample_data import (
    competitions,
    seasons,
    grounds,
    teams,
    players,
    fixtures,
    goals,
    standings,
)

app = FastAPI()
'''
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/teams")
def read_teams(db: Session = Depends(get_db)):
    query = text("SELECT id, name, ground_id FROM teams")
    result = db.execute(query).fetchall()
    teams = [dict(row) for row in result]
    if not teams:
        raise HTTPException(status_code=404, detail="No teams found")
    return teams
'''
@app.get("/competitions")
def get_competitions():
    if not competitions:
        raise HTTPException(status_code=404, detail="No competitions found")
    return competitions

@app.get("/seasons")
def get_seasons():
    if not seasons:
        raise HTTPException(status_code=404, detail="No seasons found")
    return seasons

@app.get("/grounds")
def get_grounds():
    if not grounds:
        raise HTTPException(status_code=404, detail="No grounds found")
    return grounds

@app.get("/teams")
def get_teams():
    if not teams:
        raise HTTPException(status_code=404, detail="No teams found")
    return teams

@app.get("/players")
def get_players():
    if not players:
        raise HTTPException(status_code=404, detail="No players found")
    return players

@app.get("/fixtures")
def get_fixtures():
    if not fixtures:
        raise HTTPException(status_code=404, detail="No fixtures found")
    return fixtures

@app.get("/goals")
def get_goals():
    if not goals:
        raise HTTPException(status_code=404, detail="No goals found")
    return goals

@app.get("/standings")
def get_standings():
    if not standings:
        raise HTTPException(status_code=404, detail="No standings found")
    return standings
