from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from datetime import datetime, timedelta, timezone
from database import get_db

router = APIRouter(prefix="/api/v1", tags=["fetch_news_list"])

@router.get("/news")
def fetch_news_list(
    limit: Optional[int] = Query(10, description="1~30"),
    locale: Optional[str] = Query("en-US", description="support only ko-KR, en-US"),
    db: Session = Depends(get_db),
): 
    sql = """
        SELECT
            id,
            title_en,
            title_kr,
            content_en,
            content_kr,
            thumbnail_url,
            publish_date,
            author_en,
            author_kr,
            source,
            url
        FROM news
        LIMIT :limit
    """
    rows = db.execute(text(sql), {"limit": limit}).fetchall()
   
    sql_total = "SELECT COUNT(*) AS total FROM news"
    total = db.execute(text(sql_total)).scalar()

    
    news_list = []
    for r in rows:
        news_list.append({
            "id": r.id,
            "title": r.title_kr if locale == "ko-KR" else r.title_en,
            "content": r.content_kr if locale == "ko-KR" else r.content_en,
            "thumbnailUrl": r.thumbnail_url,
            "publishDate": r.publish_date,
            "author": r.author_kr if locale == "ko-KR" else r.author_en,
            "source": r.source,
            "url": r.url,
        })   

    KST = timezone(timedelta(hours=9))
    #last_updated = datetime.now(KST).isoformat()
    last_updated = datetime.now(KST).strftime("%Y-%m-%dT%H:%M:%S")

    return {
        "news": news_list,
        "meta": {
            "locale": locale,
            "lastUpdated": last_updated,
            "pagination": {
                "total": limit
            }
        }
    }