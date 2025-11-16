from sqlalchemy.orm import Session
from sqlalchemy import text
from datetime import datetime

def web_to_db_season(web_season: str) -> str:
    """
    웹에서 입력받은 시즌 (예: '2024-25') → DB 시즌 형식 ('24/25') 변환
    """
    start, end = web_season.split("-")
    return f"{start[2:]}/{end}"   # "2024-25" → "24/25"


def get_season_id_by_abbr(db: Session, competition_id: str, season_db: str):
    """
    season abbreviation + competition_id → season.id 조회
    """
    sql = text("""
        SELECT id
        FROM seasons
        WHERE abbreviation = :abbr
          AND competition_id = :cid
        LIMIT 1
    """)

    row = db.execute(sql, {"abbr": season_db, "cid": competition_id}).fetchone()
    return row._mapping["id"] if row else None


def get_current_or_latest_season_id(db: Session, competition_id: str):
    """
    현재 날짜 기준으로:
    - 시즌 기간(date_start ~ date_end)이면 해당 시즌 ID 반환
    - 시즌 기간이 아니면 가장 최신 시즌 ID 반환
    """
    now = datetime.now()

    # 1) 현재 날짜가 포함된 시즌 조회
    sql_current = text("""
        SELECT id
        FROM seasons
        WHERE competition_id = :cid
          AND date_start <= :now
          AND date_end >= :now
        LIMIT 1
    """)

    row = db.execute(sql_current, {"cid": competition_id, "now": now}).fetchone()
    if row:
        return row._mapping["id"]

    # 2) 시즌 기간이 아니라면 → 최신 시즌
    sql_latest = text("""
        SELECT id
        FROM seasons
        WHERE competition_id = :cid
        ORDER BY date_start DESC
        LIMIT 1
    """)

    row = db.execute(sql_latest, {"cid": competition_id}).fetchone()
    return row._mapping["id"] if row else None