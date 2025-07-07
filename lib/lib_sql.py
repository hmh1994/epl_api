from pathlib import Path

def load_sql(file_path: str) -> str:
    sql_dir = Path(__file__).resolve().parent.parent / "sql"
    full_path = sql_dir / file_path
    return full_path.read_text(encoding='utf-8')
