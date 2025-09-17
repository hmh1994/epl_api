from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel, create_model
from typing import List, Optional, Any
from lib.lib_database import get_db

router = APIRouter(prefix="/api/v1/base", tags=["Base"])

# DB 컬럼 → (API 키, 타입)
dp_to_api = {
    "id": ("key", int),
    "abbreviation": ("abbr", str),
    "name": ("name", str),
    "season": ("season", Optional[int]),
}

# Pydantic 모델 자동 생성
fields = {v[0]: (v[1], ...) for v in dp_to_api.values()}  # ... = 필수 필드
Competition = create_model("Competition", **fields)

class CompetitionResponse(BaseModel):
    competitions: List[Competition]

@router.get("/competitions_auto", response_model=CompetitionResponse)
def get_competitions(db: Session = Depends(get_db)):
    sql = "SELECT * FROM competitions"
    query = db.execute(text(sql))
    
    competitions = []
    for row in query.fetchall():
        row_dict = dict(row._mapping)
        api_row = {dp_to_api.get(k, (k, Any))[0]: v for k, v in row_dict.items()}
        competitions.append(api_row)
    
    return {"competitions": competitions}