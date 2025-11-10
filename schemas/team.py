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
    pass

class TeamsInfoResponse(BaseModel):
    TeamSummary: List[TeamSummary]
    meta: dict 
