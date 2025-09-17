from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from lib.lib_database import get_db

router = APIRouter(prefix="/api/v1/dataVerify", tags=["Verify"])

@router.get("/match_stats")
def table_match_stats(db: Session = Depends(get_db)):
    sql = "SELECT * FROM match_stats LIMIT 1"
    query = db.execute(text(sql))
    return {"match_stats": [dict(row._mapping) for row in query.fetchall()]}

