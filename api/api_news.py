from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import text 
from lib.lib_database import get_db
from lib.lib_camel import dict_to_camel_case
from lib.lib_sql import load_sql

router = APIRouter(prefix="/api/v1/news", tags=["News"])

@router.get("/list")
def news_list(db: Session = Depends(get_db)):
    sql = load_sql("news_list.sql")
    query = text(sql)    
    result = db.execute(query).fetchall()
    return {
        "newsList": [dict_to_camel_case(row._mapping) for row in result]
    }
