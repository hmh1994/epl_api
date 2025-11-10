from sqlalchemy.orm import Session
from typing import List, Optional
from utils.response_builder import map_row

def get_teams(
    db: Session,
    league_id: Optional[str] = None,
    search: Optional[str] = None
) -> List[dict]:
    """
    DB에서 팀 정보를 조회하고, 웹 키로 매핑
    """
    sql = "SELECT * FROM teams"
    params = {}

    filters = []
    if league_id:
        filters.append("source_id = :league_id")  # league_id와 source_id 매핑 예시
        params["league_id"] = league_id
    if search:
        filters.append("(name_en ILIKE :search OR abbreviation ILIKE :search OR name_kr ILIKE :search)")
        params["search"] = f"%{search}%"

    if filters:
        sql += " WHERE " + " AND ".join(filters)

    rows = db.execute(sql, params).fetchall()

    mapping = {
        "id": "id",
        "name_en": "name",
        "short_name_en": "shortName",
        "icon_url": "crest",
        "city_name_en": "city",
        "stadium": "stadium"
    }

    return [map_row(dict(row), mapping) for row in rows]
