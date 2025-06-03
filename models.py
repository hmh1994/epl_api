from sqlalchemy import Column, Integer, String, DateTime
from database import Base

class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    title_en = Column(String)
    title_kr = Column(String)
    content_en = Column(String)
    content_kr = Column(String)
    url = Column(String)
    thumbnail_url = Column(String)
    source = Column(String)
    type = Column(String)
    publish_date = Column(DateTime)