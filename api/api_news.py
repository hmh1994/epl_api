from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.inspection import inspect
from lib.lib_database import get_db
from lib.lib_models import News

router = APIRouter(prefix="/api/v1/news", tags=["News"])  # 반드시 이 부분 있어야 함

def orm_to_dict(obj):
    return {c.key: getattr(obj, c.key) for c in inspect(obj).mapper.column_attrs}

@router.get("/list")
def news_list(db: Session = Depends(get_db)):
    news_list = db.query(News).order_by(News.publishDate.desc()).all()
    return {"newsList": [dict(orm_to_dict(n)) for n in news_list]}