import os

DB_URL = os.getenv(
    "DATABASE_URL",
    "postgresql+psycopg2://postgres:abcd@football-data-v1.cb0kwomosfy3.ap-northeast-2.rds.amazonaws.com:5432/postgres"
)

DEFAULT_LOCALE = "ko-KR"

LEAGUE_MAP = {
    "EPL": "EN_PR",
}