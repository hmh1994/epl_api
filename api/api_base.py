from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel
from typing import List, Optional
from lib.lib_database import get_db

router = APIRouter(prefix="/api/v1/base", tags=["Base"])

# DB 컬럼 → API 키 매핑
dp_to_api = {
    "id": "key",
    "abbreviation": "abbr",
    "name": "name",
    "season": "season",
}

# Pydantic 모델 정의
class Competition(BaseModel):
    key: int
    abbr: str
    name: str
    season: Optional[int] = None  # None 가능하면 Optional

class CompetitionResponse(BaseModel):
    competitions: List[Competition]

@router.get("/competitions2", response_model=CompetitionResponse)
def get_competitions(db: Session = Depends(get_db)):
    sql = "SELECT * FROM competitions"
    query = db.execute(text(sql))
    
    competitions = []
    for row in query.fetchall():
        row_dict = dict(row._mapping)
        api_row = {dp_to_api.get(k, k): v for k, v in row_dict.items()}
        competitions.append(api_row)
    
    return {"competitions": competitions}