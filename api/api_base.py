from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from lib.lib_database import get_db

router = APIRouter(prefix="/api/v1/dataVerify", tags=["Verify"])

@router.get("/match_stats", response_model=list[dict])
def table_match_stats(db: Session = Depends(get_db)) -> list[dict]:
    sql = """
    SELECT 
        *
    FROM match_stats
    LIMIT 5
    """
    query = db.execute(text(sql))
    results = [dict(row._mapping) for row in query.fetchall()]

    for row in results:
        match_id = row["match_id"]
        extra_data = get_additional_info(match_id, db)
        row["matches"] = extra_data 

    return results

def get_additional_info(match_id: str, db: Session) -> list[dict]:
    sql = """
    SELECT *
    FROM matches
    WHERE id = :match_id
    """
    query = db.execute(text(sql), {"match_id": match_id})
    rows = query.fetchall()
    return [dict(row._mapping) for row in rows]