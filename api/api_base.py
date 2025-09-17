from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from lib.lib_database import get_db

router = APIRouter(prefix="/api/v1/base", tags=["Base"])

@router.get("/competitions")
def get_competitions(db: Session = Depends(get_db)):
    sql = "SELECT * FROM competitions"
    query = db.execute(text(sql))
    competitions = [dict(row._mapping) for row in query.fetchall()]
    return {"competitions": competitions}