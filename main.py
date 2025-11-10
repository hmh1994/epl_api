'''from fastapi import FastAPI
#from api.api_database import router as database_router

app = FastAPI(title="Football Data API", version="1.0",)

#app.include_router(database_router)
'''

from fastapi import FastAPI, Depends, Query
from sqlalchemy.orm import Session
from utils.league import map_league_id
from utils.time import current_millis
from database import get_db

from crud import teams, leagues, matches, players

app = FastAPI(title="Football API")

# ---------------- Teams ----------------
@app.get("/api/v1/teams")
async def api_teams(leagueId: str = None, search: str = None, db: Session = Depends(get_db)):
    league_db_id = map_league_id(leagueId) if leagueId else None
    data = await teams.get_teams(db, league_db_id, search)
    return {"data": data, "meta": {"total": len(data), "lastUpdated": current_millis()}}

# ---------------- League Metadata ----------------
@app.get("/api/v1/leagues/{leagueId}/metadata")
async def api_league_metadata(leagueId: str, season: str = Query(...), db: Session = Depends(get_db)):
    league_db_id = map_league_id(leagueId)
    data = await leagues.get_league_metadata(db, league_db_id, season)
    return {"data": data, "meta": {"leagueId": leagueId, "season": season, "lastUpdated": current_millis()}}

# ---------------- League Standings ----------------
@app.get("/api/v1/leagues/{leagueId}/standings")
async def api_league_standings(leagueId: str, season: str = Query(...), includeAdvanced: bool = False, db: Session = Depends(get_db)):
    league_db_id = map_league_id(leagueId)
    data = await leagues.get_league_standings(db, league_db_id, season, includeAdvanced)
    return {"data": data, "meta": {"leagueId": leagueId, "season": season, "lastUpdated": current_millis()}}

# ---------------- Match Schedule ----------------
@app.get("/api/v1/leagues/{leagueId}/schedule")
async def api_match_schedule(leagueId: str, season: str = Query(...), matchweek: int = None, db: Session = Depends(get_db)):
    league_db_id = map_league_id(leagueId)
    data = await matches.get_match_schedule(db, league_db_id, season, matchweek)
    return {"data": data, "meta": {"leagueId": leagueId, "season": season, "lastUpdated": current_millis()}}

# ---------------- Match Detail ----------------
@app.get("/api/v1/matches/{matchId}")
async def api_match_detail(matchId: str, db: Session = Depends(get_db)):
    data = await matches.get_match_detail(db, matchId)
    return {"data": data, "meta": {"matchId": matchId, "lastUpdated": current_millis()}}

# ---------------- Player Database ----------------
@app.get("/api/v1/leagues/{leagueId}/players/database")
async def api_player_database(leagueId: str, season: str = Query(...), teamId: str = None, db: Session = Depends(get_db)):
    league_db_id = map_league_id(leagueId)
    data = await players.get_player_database(db, league_db_id, season, teamId)
    return {"data": data, "meta": {"leagueId": leagueId, "season": season, "lastUpdated": current_millis()}}

# ---------------- Team Profiles ----------------
@app.get("/api/v1/leagues/{leagueId}/teams/profiles")
async def api_team_profiles(leagueId: str, season: str = Query(...), db: Session = Depends(get_db)):
    league_db_id = map_league_id(leagueId)
    data = await teams.get_teams(db, league_db_id)
    return {"data": data, "meta": {"leagueId": leagueId, "season": season, "lastUpdated": current_millis()}}

# ---------------- Team Squad ----------------
@app.get("/api/v1/teams/{teamId}/squad")
async def api_team_squad(teamId: str, season: str = Query(...), db: Session = Depends(get_db)):
    data = await teams.get_team_squad(db, teamId, season)
    return {"data": data, "meta": {"teamId": teamId, "season": season, "lastUpdated": current_millis()}}

# ---------------- Hub Overview ----------------
@app.get("/api/v1/leagues/{leagueId}/hub-overview")
async def api_hub_overview(leagueId: str, season: str = Query(...), limitFixtures: int = 3, limitRankings: int = 5, db: Session = Depends(get_db)):
    league_db_id = map_league_id(leagueId)
    standings = await leagues.get_league_standings(db, league_db_id, season)
    fixtures = await matches.get_match_schedule(db, league_db_id, season)
    player_rankings = await players.get_player_database(db, league_db_id, season)
    return {
        "data": {
            "standings": standings[:limitRankings],
            "featuredFixtures": fixtures[:limitFixtures],
            "playerRankings": player_rankings[:limitRankings]
        },
        "meta": {"leagueId": leagueId, "season": season, "generatedAt": current_millis()}
    }
