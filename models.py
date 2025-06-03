from sqlalchemy import Column, Integer, String, DateTime
from database import Base

class News(Base):
    __tablename__ = "news"

    id = Column("id", Integer, primary_key=True, index=True)
    titleEnglish = Column("title_en", String)
    titleKorean = Column("title_kr", String)
    contentEnglish = Column("content_en", String)
    contentKorean = Column("content_kr", String)
    url = Column("url", String)
    thumbnailUrl = Column("thumbnail_url", String)
    source = Column("source", String)
    type = Column("type", String)
    publishDate = Column("publish_date", DateTime)