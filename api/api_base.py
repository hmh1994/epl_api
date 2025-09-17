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
        populate_by_name = True   # alias 변환 허용
        from_attributes = True    # ORM 객체도 처리 가능
        orm_mode = True           # SQLAlchemy ORM 모델 지원
        extra = "ignore"          # 모델에 정의되지 않은 필드는 무시


@router.get(
    "/competitions",
    response_model=List[CompetitionResponse],
    response_model_by_alias=True   # ✅ docs와 응답 JSON에 alias 반영
)
def get_competitions(db: Session = Depends(get_db)):
    sql = """
        SELECT id, abbreviation, name_en, name_kr,
               description_en, description_kr, icon_url,
               source, source_id, created_at, updated_at
        FROM competitions
    """
    query = text(sql)
    result = db.execute(query).fetchall()

    # Row -> Pydantic 모델 변환
    competitions = [CompetitionResponse(**row._mapping) for row in result]
    return competitions