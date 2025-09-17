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


# DB 컬럼 → API 키 + 타입 매핑
dp_to_api = {
    "id": ("str", int),
    "abbreviation": ("abbr", str),

}

@router.get("/competitions2")
def get_competitions(db: Session = Depends(get_db)):
    sql = "SELECT * FROM competitions"
    query = db.execute(text(sql))
    
    competitions = []
    for row in query.fetchall():
        row_dict = dict(row._mapping)
        api_row = {}
        for col, value in row_dict.items():
            if col in dp_to_api:
                key, typ = dp_to_api[col]
                try:
                    api_row[key] = typ(value) if value is not None else None
                except Exception:
                    api_row[key] = value  # 변환 실패 시 원래 값 유지
            else:
                api_row[col] = value
        competitions.append(api_row)
    
    return {"competitions": competitions}