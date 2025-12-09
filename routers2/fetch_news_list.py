from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from database import get_db

router = APIRouter(prefix="/api/v1", tags=["fetch_news_list"])

@router.get("/news")
def fetch_news_list(
    limit: Optional[int] = Query(10, description="1~30"),
    locale: Optional[str] = Query("en-US", description="support only ko-KR, en-US"),
): 
    return 0