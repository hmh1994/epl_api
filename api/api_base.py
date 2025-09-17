from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from lib.lib_database import get_db

router = APIRouter(prefix="/api/v1/dataVerify", tags=["Verify"])

@router.get("/match_stats", response_model=list[dict])
def table_match_stats(db: Session = Depends(get_db)) -> list[dict]:
    sql = "SELECT * FROM match_stats LIMIT 1"
    query = db.execute(text(sql))
    results = [dict(row._mapping) for row in query.fetchall()]
    return results