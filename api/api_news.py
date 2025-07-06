from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy.sql import text 
from lib.lib_database import get_db
from lib.lib_camel import dict_to_camel_case


router = APIRouter(prefix="/api/v1/news", tags=["News"])

@router.get("/list")
def news_list(db: Session = Depends(get_db)):
    query = text("""
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
            STRING_AGG(t.name_en, ', ') AS team_name_en,
            STRING_AGG(t.name_kr, ', ') AS team_name_kr,
            n.type,
            n.publish_date
        FROM news_new n
        LEFT JOIN news_team_association nta ON nta.news_id = n.id
        LEFT JOIN teas_new t ON t.id = nta.team_id
        GROUP BY 
        n.id, n.title_en, n.title_kr, n.content_en, n.content_kr,
        n.thumbnail_url, n.url, n.author_en, n.author_kr, n.type, n.publish_date
        ORDER BY n.publish_date DESC
    """)
    
    result = db.execute(query).fetchall()
    return {
        "newsList": [dict_to_camel_case(row._mapping) for row in result]
    }