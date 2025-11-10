from fastapi import FastAPI
from routers import teams

app = FastAPI(title="Football Data API", version="1.0",)

app.include_router(teams.router)
#from api.api_database import router as database_router
#app.include_router(database_router)