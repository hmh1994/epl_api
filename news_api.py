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
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.inspection import inspect
from database import get_db
from models import News
from model import dict_to_camel_case

router = APIRouter(prefix="/api/v1/news", tags=["News"])  # 반드시 이 부분 있어야 함

def orm_to_dict(obj):
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}

@router.get("/list")
def news_list(db: Session = Depends(get_db)):
    news_list = db.query(News).order_by(News.publish_date.desc()).all()
    return {"newsList": [dict_to_camel_case(orm_to_dict(n)) for n in news_list]}