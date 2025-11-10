from sqlalchemy.orm import Session
from utils.response_builder import map_row

def get_league_metadata(db: Session, league_id: str, season: str):
    sql = """
        SELECT 
            id as league_id,
            name_en as league_name,
            name_kr,
            abbreviation,
            icon_url as logo,
            description_en,
            description_kr,
            created_at,
            updated_at
        FROM competitions
        WHERE id = :league_id
    """
    row = db.execute(sql, {"league_id": league_id}).fetchone()
    if not row:
        return None

    mapping = {
        "league_id": "leagueId",
        "league_name": "name",
        "icon": "logo",
        "abbreviation": "abbreviation",
        "description_en": "descriptionEn",
        "description_kr": "descriptionKr",
        "created_at": "createdAt",
        "updated_at": "updatedAt",
    }

    return map_row(dict(row), mapping)