from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import text  
from database import get_db
from model import dict_to_camel_case

router = APIRouter(prefix="/api/v1/news", tags=["News"])

@router.get("/newsList")
def player_rank(db : Session = Depends(get_db)):
    query = text("SELECT * from news ORDER BY publishDate DESC LIMIT 3")
    result = db.execute(query).fetchall()
    return {"newsList" : [dict_to_camel_case(row._mapping) for row in result]}
