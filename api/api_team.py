from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import text 
from lib.lib_database import get_db
from lib.lib_camel import dict_to_camel_case
from lib.lib_sql import load_sql

router = APIRouter(prefix="/api/v1/teams", tags=["Teams"])

@router.get("/rank")
def teamrank(db : Session = Depends(get_db)):
    sql = load_sql("team_rank.sql")
    query = text(sql)   
    result = db.execute(query).fetchall()
    return {"TeamRank" : [dict_to_camel_case(row._mapping) for row in result]}


@router.get("/rank/detail")
def teamrank_detail(db : Session = Depends(get_db)):
    sql = load_sql("team_rank_detail.sql")
    query = text(sql)   
    result = db.execute(query).fetchall()
    return {"TeamRankDetail" : [dict_to_camel_case(row._mapping) for row in result]}

@router.get("/info")
def teaminfo(db: Session = Depends(get_db)):
    sql = load_sql("test.sql")
    query = text(sql)   
    result = db.execute(query).fetchall()
    return {"TeamInfo" : [dict_to_camel_case(row._mapping) for row in result]}
