from fastapi import FastAPI
from routers.team_info_01 import router as TeamRouter
#from router.league_meta_02 import router as LeagueRouter

app = FastAPI(title="Football Data API", version="1.0",)

app.include_router(TeamRouter)
#app.include_router(LeagueRouter)

#app.include_router()