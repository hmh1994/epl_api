from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from lib.lib_database import get_db
from model_news import NewsItem, NewsListResponse

router = APIRouter(prefix="/api/v1/news", tags=["News"])

@router.get("/list", response_model=NewsListResponse)
def news_list(count: int = Query(..., description="Integer"), db: Session = Depends(get_db)):
    query = text(
        """
        SELECT
            n.id,
            n.title_en,
            n.title_kr,
            n.content_en,
            n.content_kr,
            n.thumbnail_url,
            n.url,
            ARRAY[n.author_en] AS author_en,
            ARRAY[n.author_kr] AS author_kr,
            ARRAY_AGG(DISTINCT t.abbreviation) AS team,
            n.type,
            n.publish_date
        FROM news n
        LEFT JOIN news_team_association nta ON nta.news_id = n.id
        LEFT JOIN teams t ON t.id = nta.team_id
        GROUP BY 
            n.id, n.title_en, n.title_kr, n.content_en, n.content_kr,
            n.thumbnail_url, n.url, n.author_en, n.author_kr, n.type, n.publish_date
        ORDER BY n.publish_date DESC
        LIMIT :count
        """
    )
    result = db.execute(query, {"count": count}).fetchall()

    news_list = [NewsItem(**dict(row._mapping)) for row in result]

    return {"newsList": news_list}
