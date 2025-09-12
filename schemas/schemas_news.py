from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

def to_camel(string: str) -> str:
    parts = string.split('_')
    return parts[0] + ''.join(word.capitalize() for word in parts[1:])

class CamelModel(BaseModel):
    class Config:
        alias_generator = to_camel
        populate_by_name = True
        orm_mode = True

class NewsBase(CamelModel):
    id: str
    title_en: Optional[str] = None
    title_kr: Optional[str] = None
    content_en: Optional[str] = None
    content_kr: Optional[str] = None
    thumbnail_url: Optional[str] = None
    url: Optional[str] = None
    author_en: Optional[List[str]] = None
    author_kr: Optional[List[str]] = None
    team: List[str] = []
    type: Optional[str] = None
    publish_date: datetime