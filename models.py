from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    titleEn = Column("title_en", String)
    titleKr = Column("title_kr", String)
    contentEn = Column("content_en", Text)
    contentKr = Column("content_kr", Text)
    newsLink = Column(String)
    titleImage = Column("thumbnail_url", String)
    source = Column(String)
    type = Column(String)
    publishDate = Column("publish_date", DateTime)