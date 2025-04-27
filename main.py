from fastapi import FastAPI
from player_api import router as players_router
from teams_api import router as teams_router
from games_api import router as games_router
from news_api import router as news_router
from database_api import router as database_router


app = FastAPI()

app.include_router(players_router)
app.include_router(teams_router)
app.include_router(games_router)
app.include_router(news_router)
app.include_router(database_router)

@app.get("/")
def root():
    return {"ROOT"}

