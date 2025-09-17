from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from lib.lib_database import get_db

router = APIRouter(prefix="/api/v1/base", tags=["Base"])

# DB 컬럼 ↔ API 이름 mapping
db_to_api = {
    "id": "key"
}

def map_keys(row: dict, mapping: dict):
    return {mapping.get(k, k): v for k, v in row.items()}

def rows_to_dict_by_key(rows: list[dict], key: str, mapping: dict):
    return {row[key]: map_keys(row, mapping) for row in rows}

@router.get("/competitions")
def get_competitions(db: Session = Depends(get_db)):
    sql = "SELECT * FROM competitions"
    query = text(sql)
    
    # SQL 실행 후 dict 형태로 변환
    rows = db.execute(query).mappings().all()
    
    # id를 key로 하는 dict 생성
    api_result = rows_to_dict_by_key(rows, "id", db_to_api)
    
    return api_result