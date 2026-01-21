from fastapi import FastAPI



from routers2.fetch_premium_table import router as premiumRouter
from routers2.fetch_match_schedule import router as scheduleRouter
from routers2.fetch_player_list import router as playerListRouter
from routers2.fetch_season_analytics import router as seasonRouter
from routers2.fetch_team_detail import router as teamRouter
from routers2.fetch_player_detail import router as playerRouter
from routers2.fetch_scoring_race import router as scoringRouter
from routers2.fetch_news_list import router as newsRouter

from routers.team_info_01 import router as Router1
from routers.league_meta_02 import router as Router2
from routers.league_rank_03 import router as Router3
from routers.hub_home_04 import router as Router4
from routers.league_pulse_05 import router as Router5
from routers.player_rank_06 import router as Router6
from routers.schedule_07 import router as Router7
from routers.match_detail_08 import router as Router8
from routers.player_db_09 import router as Router9
from routers.team_detail_10 import router as Router10


from api.api_database import router as database_router

app = FastAPI(title="Football Data API", version="1.0",)
app.include_router(premiumRouter)
app.include_router(scheduleRouter)
app.include_router(playerListRouter)
app.include_router(seasonRouter)
app.include_router(teamRouter)
app.include_router(playerRouter)
app.include_router(scoringRouter)
app.include_router(newsRouter)



app.include_router(Router1)
app.include_router(Router2)
app.include_router(Router3)
#app.include_router(Router4)
app.include_router(Router5)
app.include_router(Router6)
#app.include_router(Router7)
#app.include_router(Router8)
app.include_router(Router9)
app.include_router(Router10)

app.include_router(database_router)
