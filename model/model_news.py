from pydantic import BaseModel, Field, HttpUrl
from typing import List
from datetime import datetime

class NewsItem(BaseModel):
    newsId: str = Field(..., alias="id")
    titleEn: str = Field(..., alias="title_en")
    titleKr: str = Field(..., alias="title_kr")
    contentEn: str = Field(..., alias="content_en")
    contentKr: str = Field(..., alias="content_kr")
    thumbnailUrl: HttpUrl = Field(..., alias="thumbnail_url")
    url: HttpUrl
    authorEn: List[str] = Field(..., alias="author_en")
    authorKr: List[str] = Field(..., alias="author_kr")
    teams: List[str] = Field(..., alias="team")
    newsType: str = Field(..., alias="type")
    publishDate: datetime = Field(..., alias="publish_date")

    class Config:
        allow_population_by_field_name = True 

class NewsListResponse(BaseModel):
    newsList: List[NewsItem]
