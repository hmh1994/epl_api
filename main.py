from fastapi import FastAPI
from api.api_player import router as players_router
from api.api_team import router as teams_router
from api.api_fixture import router as match_router
from api.api_news import router as news_router
from api.api_database import router as database_router

app = FastAPI()

app.include_router(news_router)
app.include_router(players_router)
app.include_router(match_router)
app.include_router(teams_router)
app.include_router(database_router)
