from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import text 
from lib.lib_database import get_db
from lib.lib_camel import dict_to_camel_case


router = APIRouter(prefix="/api/v1/news", tags=["News"])

@router.get("/news")
def news_list(db: Session = Depends(get_db)):
    query = text("""
        select                  
            publish_date as publishDate,
            author_kr,
            content_en,
            content_kr,
            url,
            source,
            teams,
            thumbnail_url,
            title_en,
            title_kr,
            type,
            id,
            author_en,
            source_id
        from news
        order by publish_date DESC
    """)
    
    result = db.execute(query).fetchall()
    return {
        "newsList": [dict_to_camel_case(row._mapping) for row in result]
    }