from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from pydantic import BaseModel, Field
from typing import List
from lib.lib_database import get_db

router = APIRouter(prefix="/api/v1/base", tags=["Base"])

class CompetitionResponse(BaseModel):
    key: str = Field(..., alias="id")          # DB 컬럼 'id'를 JSON에서 'key'로
    #content_en: str = Field(..., alias="contentEn")
    #content_ko: str = Field(..., alias="contentKo")

    model_config = {
        "from_attributes": True,                # from_orm() 허용
        "populate_by_name": True                # alias 적용 가능
    }

@router.get("/competitions", response_model=List[CompetitionResponse])
def get_competitions(db: Session = Depends(get_db)):
    sql = "SELECT * FROM competitions"
    query = text(sql)
    result = db.execute(query).fetchall()

    competitions = [CompetitionResponse.from_orm(row._mapping) for row in result]
    return competitions
