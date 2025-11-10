from typing import List
from pydantic import BaseModel

class TeamSummary(BaseModel):
    id: str
    name: str
    shortName: str
    crest: str
    city: str = None
    stadium: str = None

class TeamsInfoResponse(BaseModel):
    data: List[TeamSummary]
    meta: dict
