from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel, Field
from typing import List
from lib.lib_database import get_db

router = APIRouter(prefix="/api/v1/base", tags=["Base"])

class CompetitionResponse(BaseModel):
    key: int = Field(..., alias="id")          # DB 컬럼 'id'를 JSON에서 'key'로

    class Config:
        orm_mode = True
        allow_population_by_field_name = True  # alias로도 입력 가능하게

@router.get("/competitions", response_model=List[CompetitionResponse])
def get_competitions(db: Session = Depends(get_db)):
    sql = "SELECT id FROM competitions"
    query = text(sql)
    result = db.execute(query).fetchall()

    # Row -> dict -> Pydantic 모델
    competitions = [CompetitionResponse.from_orm(row._mapping) for row in result]
    return competitions
