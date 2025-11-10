from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base

from config import DB_URL

engine = create_engine(DB_URL, echo=True, future=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def execute_raw(db, sql: str, params: dict = None):
    stmt = text(sql)
    result = db.execute(stmt, params or {})
    return [dict(row) for row in result.fetchall()]