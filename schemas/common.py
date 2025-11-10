from typing import Optional, List, Generic, TypeVar
from pydantic import BaseModel

T = TypeVar("T")

class ApiResponseMeta(BaseModel):
    season: Optional[str]
    lastUpdated: Optional[int]
    leagueId: Optional[str]
    leagueName: Optional[str]
    locale: Optional[str]

class ApiListResponse(BaseModel, Generic[T]):
    data: List[T]
    meta: Optional[ApiResponseMeta] = None

class ApiResourceResponse(BaseModel, Generic[T]):
    data: T
    meta: Optional[ApiResponseMeta] = None
