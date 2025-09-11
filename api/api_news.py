'''from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import text 
from lib.lib_database import get_db
from lib.lib_camel import dict_to_camel_case
from lib.lib_sql import load_sql
from fastapi import Query

router = APIRouter(prefix="/api/v1/news", tags=["News"])

@router.get("/list")
def news_list(count: int = Query(..., description="Integer"), db: Session = Depends(get_db)):
    sql = load_sql("news_list.sql")
    query = text(sql)    
    result = db.execute(query, {"count": count}).fetchall()
    return {
        "newsList": [dict_to_camel_case(row._mapping) for row in result]
    }'''
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from lib.lib_database import get_db
from lib.lib_camel import dict_to_camel_case

router = APIRouter(prefix="/api/v1/news", tags=["News"])

# --------------------------
# 하위 API 함수
# --------------------------

def get_news_basic(db: Session, count: int):
    sql = """
    SELECT
        n.id AS news_id,
        n.title_en,
        n.title_kr,
        n.content_en,
        n.content_kr,
        n.thumbnail_url AS news_img,
        n.url AS news_url,
        n.author_en,
        n.author_kr,
        n.type,
        n.publish_date
    FROM news n
    ORDER BY n.publish_date DESC
    LIMIT :count
    """
    result = db.execute(text(sql), {"count": count}).fetchall()
    return [dict_to_camel_case(row._mapping) for row in result]

def get_news_teams(db: Session, news_ids: list[int]):
    if not news_ids:
        return {}
    sql = """
    SELECT
        nta.news_id,
        ARRAY_AGG(DISTINCT t.abbreviation) AS team
    FROM news_team_association nta
    JOIN teams t ON t.id = nta.team_id
    WHERE nta.news_id = ANY(:news_ids)
    GROUP BY nta.news_id
    """
    result = db.execute(text(sql), {"news_ids": news_ids}).fetchall()
    return {row.news_id: row.team for row in result}



@router.get("/list")
def news_list(count: int = Query(..., description="Number of news items"), db: Session = Depends(get_db)):
    news_basic = get_news_basic(db, count)
    news_ids = [news["newsId"] for news in news_basic]
    teams_map = get_news_teams(db, news_ids)
    for news in news_basic:
        news["team"] = teams_map.get(news["newsId"], [])

    return {"newsList": news_basic}