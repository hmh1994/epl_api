from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import Optional
from database import get_db

router = APIRouter(prefix="/api/v1", tags=["referee_info"])

KST = timezone(timedelta(hours=9))


@router.get("/officials/{officialId}/stats")
def referee_info(
    officialId: str,
    locale: Optional[str] = Query("en-US"),
    db: Session = Depends(get_db),
):

    referee_sql = text("""
        SELECT 
            id,
            display_name_en,
            display_name_kr,
            full_name
        FROM officials
        WHERE id = :official_id
    """)

    referee_row = db.execute(
        referee_sql,
        {"official_id": officialId}
    ).fetchone()

    if not referee_row:
        return {"error": "Official not found"}

    official = {
        "id": referee_row.id,
        "displayName": referee_row.display_name_en if locale == "en-US" else referee_row.display_name_kr,
        "fullName": referee_row.full_name
    }

    return {
        "official": official,
        "meta": {
            "officialId": officialId,
            "locale": locale,
            "lastUpdated": datetime.now(KST).strftime("%Y-%m-%dT%H:%M:%S")
        }
    }