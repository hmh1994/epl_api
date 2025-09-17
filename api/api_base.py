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


dp_to_api = {
    "id": "key",
    "abbreviation": "abbr",
    # 필요한 컬럼 추가 가능
}

@router.get("/competitions2")
def get_competitions(db: Session = Depends(get_db)):
    sql = "SELECT * FROM competitions"
    query = db.execute(text(sql))
    
    competitions = []
    for row in query.fetchall():
        row_dict = dict(row._mapping)
        # 매핑 적용
        api_row = {dp_to_api.get(k, k): v for k, v in row_dict.items()}
        competitions.append(api_row)
    
    return {"competitions": competitions}