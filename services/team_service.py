from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional
from utils.response_builder import map_row

def get_teams(
    db: Session,
    league_id: Optional[str] = None,
    search: Optional[str] = None
) -> List[dict]:
    sql_str = "SELECT * FROM teams"
    params = {}

    filters = []
    if league_id:
        filters.append("source_id = :league_id")
        params["league_id"] = league_id
    if search:
        filters.append("(name_en ILIKE :search OR abbreviation ILIKE :search OR name_kr ILIKE :search)")
        params["search"] = f"%{search}%"

    if filters:
        sql_str += " WHERE " + " AND ".join(filters)

    sql = text(sql_str)
    rows = db.execute(sql, params).fetchall()

    mapping = {
        "id": "id",
        "name_en": "name",
        "short_name_en": "shortName",
        "icon_url": "crest",
        "city_name_en": "city",
        "stadium": "stadium"
    }

    return [map_row(dict(row._mapping), mapping) for row in rows]
