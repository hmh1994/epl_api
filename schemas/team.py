from pydantic import BaseModel
from typing import List, Optional

class TeamSummary(BaseModel):
    id: str
    name: str
    shortName: str
    crest: str
    city: Optional[str] = None
    stadium: Optional[str] = None

class ApiResponseMeta(BaseModel):
    # 필요 시 추가 정보
    pass

class TeamsInfoResponse(BaseModel):
    data: List[TeamSummary]
    meta: dict  # ApiResponseMeta + total
