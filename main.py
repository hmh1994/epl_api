from fastapi import FastAPI

app = FastAPI(title="Football Data API", version="1.0",)



app.include_router()