'''from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import text  
from database import get_db
from model import dict_to_camel_case

router = APIRouter(prefix="/api/v1/news", tags=["News"])

@router.get("/list")
def newsList(db : Session = Depends(get_db)):
    query = text("""
                 SELECT 
                    id,
                    title_en, 
                    title_kr, 
                    content_en, 
                    content_kr,
                    url,
                    thumbnail_url,
                    source,
                    type,
                    publish_date
                 from news 
                 ORDER BY publish_date DESC                 
                 """)
    result = db.execute(query).fetchall()
    return {"newsList" : [dict_to_camel_case(row._mapping) for row in result]}
'''
# news_api.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db
from models import News
from schemas import NewsListResponse

router = APIRouter(prefix="/api/v1/news", tags=["News"])

@router.get("/list", response_model=NewsListResponse)
def news_list(db: Session = Depends(get_db)):
    news_items = db.query(News).order_by(News.publish_date.desc()).all()
    return {"newsList": news_items}