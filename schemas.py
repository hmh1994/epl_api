# schemas.py
from pydantic import BaseModel
from datetime import datetime

def to_camel(string: str) -> str:
    parts = string.split('_')
    return parts[0] + ''.join(word.capitalize() for word in parts[1:])

class NewsItem(BaseModel):
    id: int
    titleEn: str
    titleKr: str
    contentEn: str
    contentKr: str
    url: str
    thumbnailUrl: str
    source: str
    type: str
    publishDate: datetime

    class Config:
        orm_mode = True
        alias_generator = to_camel
        allow_population_by_field_name = True

class NewsListResponse(BaseModel):
    newsList: list[NewsItem]