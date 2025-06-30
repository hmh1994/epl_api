from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Dict, Any
from lib.lib_database import get_db  
from lib.lib_database import engine

router = APIRouter(prefix="/api/database", tags=["Database"])
inspector = inspect(engine)
table_names = sorted(inspector.get_table_names())

for table_name in table_names:
    route_path = f"/{table_name}"

    def generate_handler(table=table_name):
        def handler(db: Session = Depends(get_db)):
            try:
                result = db.execute(text(f'SELECT * FROM "{table}"')).fetchall()
                return {table: [dict(row._mapping) for row in result]}
            except Exception as e:
                raise HTTPException(status_code=500, detail=str(e))
        return handler

    router.add_api_route(
        route_path,
        generate_handler(),
        methods=["GET"],
        name=f"get_{table_name}"
    )

@router.get("/")
def list_all_tables() -> Dict[str, List[str]]:
    return {"tables": table_names}