from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel, create_model
from typing import List, Optional, Any
from lib.lib_database import get_db

router = APIRouter(prefix="/api/v1/base", tags=["Base"])

# DB 컬럼 → (API 키, 타입)
dp_to_api = {
    "id": ("id", str),
    "abbreviation": ("abbr", str),
    "name_en" : ("nameEn", str),
    "name_kr" : ("nameKr", str),

}

fields = {v[0]: (v[1], ...) for v in dp_to_api.values()}
Competition = create_model("Competition", **fields)
class CompetitionResponse(BaseModel):
    competitions: List[Competition]

@router.get("/competitions_auto", response_model=CompetitionResponse)
def get_competitions(db: Session = Depends(get_db)):
    sql = "SELECT id, abbreviation,name_en, name_kr FROM competitions"
    query = db.execute(text(sql))
    
    competitions = []
    for row in query.fetchall():
        row_dict = dict(row._mapping)
        api_row = {dp_to_api.get(k, (k, Any))[0]: v for k, v in row_dict.items()}
        competitions.append(api_row)
    
    return {"competitions": competitions}