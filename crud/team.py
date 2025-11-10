from sqlalchemy.orm import Session
from sqlalchemy import text

def get_teams(db: Session, league_id: str = None, search: str = None):
    sql = "SELECT id, name_en, short_name_en, icon_url FROM teams WHERE 1=1"

    params = {}
    if league_id:
        sql += " AND league_id = :league_id"
        params["league_id"] = league_id
    if search:
        sql += " AND name_en ILIKE :search"
        params["search"] = f"%{search}%"

    query = db.execute(text(sql), params)
    result = query.mappings().all()  # <- 여기서 dict 형태로 변환

    teams = []
    for row in result:
        teams.append({
            "id": row["id"],
            "name": row["name_en"],
            "shortName": row["short_name_en"],
            "crest": row["icon_url"],
            "city": None,
            "stadium": None
        })

    return {"TeamSummary": teams, "meta": {"total": len(teams)}}
