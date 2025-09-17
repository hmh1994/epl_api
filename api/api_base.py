from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from lib.lib_database import get_db

router = APIRouter(prefix="/api/v1/base", tags=["Base"])

@router.get("/competitions")
def get_competitions(db: Session = Depends(get_db)):
    sql = """
        select * from competitions
    """
    query = text(sql)
    result = db.execute(query).fetchall()
    competitions = [dict(row._mapping) for row in result]
    return {"competitions": competitions}

