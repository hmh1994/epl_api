from pydantic import BaseModel
from datetime import datetime

class NewsSchema(BaseModel):
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