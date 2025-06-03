from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base  # declarative_base 추가

DB_URL = "postgresql://postgres:holders-hyah-movin-latch@football-data-v1.cb0kwomosfy3.ap-northeast-2.rds.amazonaws.com/postgres"
engine = create_engine(DB_URL, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()  # 여기서 선언

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()