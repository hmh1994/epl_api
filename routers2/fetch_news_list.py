'''from fastapi import APIRouter, Depends, Query
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
        ORDER BY publish_date DESC
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
    '''

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from datetime import datetime, timezone, timedelta
from database import get_db

router = APIRouter(prefix="/api/v1", tags=["fetch_news_list"])

@router.get("/news")
def fetch_news_list(
    pageCnt: Optional[int] = Query(1, ge=1, description="Page number (start from 1)"),
    pageSize: Optional[int] = Query(10, ge=1, le=500, description="Items per page"),
    search: Optional[str] = Query(None, description="Search by title"),
    locale: Optional[str] = Query("en-US", description="support only ko-KR, en-US"),
    db: Session = Depends(get_db),
):
    offset = (pageCnt - 1) * pageSize

    # locale 에 따른 title 컬럼 결정
    title_col = "title_kr" if locale == "ko-KR" else "title_en"
    content_col = "content_kr" if locale == "ko-KR" else "content_en"
    author_col = "author_kr" if locale == "ko-KR" else "author_en"

    # WHERE 조건 동적 구성
    where_clause = ""
    params = {
        "limit": pageSize,
        "offset": offset,
    }

    if search:
        where_clause = f"WHERE {title_col} ILIKE :search"
        params["search"] = f"%{search}%"

    # 뉴스 리스트 조회
    sql = f"""
        SELECT
            id,
            {title_col}   AS title,
            {content_col} AS content,
            thumbnail_url,
            publish_date,
            {author_col}  AS author,
            source,
            url
        FROM news
        {where_clause}
        ORDER BY publish_date DESC
        LIMIT :limit OFFSET :offset
    """

    rows = db.execute(text(sql), params).fetchall()

    # 전체 개수 조회
    sql_total = f"""
        SELECT COUNT(*) 
        FROM news
        {where_clause}
    """
    total = db.execute(text(sql_total), params).scalar()

    # 응답 데이터 구성
    news_list = []
    for r in rows:
        news_list.append({
            "id": r.id,
            "title": r.title,
            "content": r.content,
            "thumbnailUrl": r.thumbnail_url,
            "publishDate": r.publish_date,
            "author": r.author,
            "source": r.source,
            "url": r.url,
        })

    # pagination meta 계산
    has_previous = pageCnt > 1
    has_next = (offset + pageSize) < total

    # KST 기준 lastUpdated
    KST = timezone(timedelta(hours=9))
    last_updated = datetime.now(KST).strftime("%Y-%m-%dT%H:%M:%S")

    return {
        "data": news_list,
        "meta": {
            "total": total,
            "pageSize": pageSize,
            "pageCnt": pageCnt,
            "hasNext": has_next,
            "hasPrevious": has_previous,
            "locale": locale,
            "lastUpdated": last_updated,
        }
    }