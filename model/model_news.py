from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class NewsItem(BaseModel):
    newsId: str
    titleEn: str
    titleKr: Optional[str]
    contentEn: Optional[str]
    contentKr: Optional[str]
    newsImg: Optional[str]
    newsUrl: Optional[str]
    authorEn: List[str] = []
    authorKr: List[str] = []
    type: Optional[str]
    publishDate: datetime
    team: List[str] = []

class NewsListResponse(BaseModel):
    newsList: List[NewsItem]
