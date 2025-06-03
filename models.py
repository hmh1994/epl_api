from sqlalchemy import Column, Integer, String, DateTime
from database import Base

class News(Base):
    __tablename__ = "news"

    newsId = Column("id", Integer, primary_key=True, index=True)
    titleEn = Column("title_en", String)
    titleKo = Column("title_kr", String)
    contentEn = Column("content_en", String)
    contentKo = Column("content_kr", String)
    newsLink = Column("url", String)
    newsImg = Column("thumbnail_url", String)
    source = Column("source", String)
    type = Column("type", String)
    publishDate = Column("publish_date", DateTime)