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
    "name": ("name", str),      # DB에 없으면 무시됨
    "season": ("season", Optional[int]),  # DB에 없으면 무시됨
}

# DB 컬럼이 실제로 존재하는 컬럼만 Pydantic 모델 필드로 사용
def create_dynamic_model(row_dict, model_name="DynamicModel"):
    fields = {
        dp_to_api[k][0]: (dp_to_api[k][1], ...)
        for k in row_dict.keys()
        if k in dp_to_api
    }
    return create_model(model_name, **fields)

@router.get("/competitions_dynamic")
def get_competitions(db: Session = Depends(get_db)):
    sql = "SELECT * FROM competitions"
    query = db.execute(text(sql))
    
    competitions = []
    for row in query.fetchall():
        row_dict = dict(row._mapping)
        # 실제 존재하는 컬럼만 적용
        api_row = {dp_to_api[k][0]: v for k, v in row_dict.items() if k in dp_to_api}
        competitions.append(api_row)
    
    # 동적으로 모델 생성 (옵션)
    if competitions:
        Competition = create_dynamic_model(competitions[0])
        CompetitionResponse = create_model("CompetitionResponse", competitions=(List[Competition], ...))
    
    return {"competitions": competitions}
