from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from lib.lib_database import get_db

router = APIRouter(prefix="/api/v1/base", tags=["Base"])


class CompetitionResponse(BaseModel):
    key: str = Field(alias="id")
    abbr: Optional[str] = Field(alias="abbreviation")
    nameEn: Optional[str] = Field(alias="name_en")
    nameKr: Optional[str] = Field(alias="name_kr")
    descriptionEn: Optional[str] = Field(alias="description_en")
    descriptionKr: Optional[str] = Field(alias="description_kr")
    iconUrl: Optional[str] = Field(alias="icon_url")
    source: Optional[str]
    sourceId: Optional[str] = Field(alias="source_id")
    createdAt: Optional[datetime] = Field(alias="created_at")
    updatedAt: Optional[datetime] = Field(alias="updated_at")

    class Config:
        populate_by_name = True
        from_attributes = True
        orm_mode = True
        extra = "ignore"   # 모델에 정의 안 된 필드가 들어와도 무시


@router.get("/competitions", response_model=List[CompetitionResponse])
def get_competitions(db: Session = Depends(get_db)):
    sql = """
        SELECT id, abbreviation, name_en, name_kr,
               description_en, description_kr, icon_url,
               source, source_id, created_at, updated_at
        FROM competitions
    """
    query = text(sql)
    result = db.execute(query).fetchall()

    competitions = [CompetitionResponse(**row._mapping) for row in result]
    return competitions