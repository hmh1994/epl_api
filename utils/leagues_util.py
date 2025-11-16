from sqlalchemy.orm import Session
from sqlalchemy import text

LEAGUE_ENUM_MAP = {
    "EPL": "EN_PR",
    "epl": "EN_PR",
}

def get_competition_id(db: Session, leagueId: str):
    # leagueId → ENUM 변환
    if leagueId not in LEAGUE_ENUM_MAP:
        return None, f"Invalid leagueId: {leagueId}"

    league_abbr = LEAGUE_ENUM_MAP[leagueId]

    # ENUM → competition_id 조회
    sql_comp = text("""
        SELECT id
        FROM competitions
        WHERE abbreviation = :abbr
        LIMIT 1
    """)

    row = db.execute(sql_comp, {"abbr": league_abbr}).fetchone()

    if not row:
        return None, f"Competition not found for abbreviation: {league_abbr}"

    return row._mapping["id"], None