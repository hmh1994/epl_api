from fastapi import FastAPI
from routers import league_router

#from api.api_database import router as database_router

app = FastAPI(title="Football Data API", version="1.0",)

#app.include_router(database_router)

app.include_router(league_router.router)