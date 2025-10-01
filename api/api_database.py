from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Dict, Any
from lib.lib_database import get_db  
from lib.lib_database import engine

router = APIRouter(prefix="/api/database", tags=["Database"])

def get_table_info():
    inspector = inspect(engine)
    tables = {}
    for table_name in inspector.get_table_names():
        columns = inspector.get_columns(table_name)
        tables[table_name] = columns
    return tables


@router.get("/columns")
def get_columns_only():
    tables = get_table_info()
    return {
        t: [col["name"] for col in cols]
        for t, cols in tables.items()
    }

@router.get("/verify/players/{players_id}")
def verify_players(players_id: str, db: Session = Depends(get_db)) -> dict:
    sql = """
    SELECT *
    FROM players
    WHERE id = :players_id
    """
    query = db.execute(text(sql), {"players_id": players_id})
    row = query.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Player not found")

    return dict(row._mapping)

@router.get("/verify/staffs/{staffs_id}")
def verify_staffs(staffs_id: str, db: Session = Depends(get_db)) -> dict:
    sql = """
    SELECT *
    FROM staffs
    WHERE id = :staffs_id
    """
    query = db.execute(text(sql), {"staffs_id": staffs_id})
    row = query.fetchone()

    if not row:
        raise HTTPException(status_code=404, detail="Staffs not found")

    return dict(row._mapping)



'''
@router.get("/columns_type")
def get_columns_with_types():
    tables = get_table_info()
    return {
        t: [{ "name": col["name"], "type": str(col["type"]) } for col in cols]
        for t, cols in tables.items()
    }

@router.get("/columns_type_null")
def get_columns_with_types_nullable():
    tables = get_table_info()
    return {
        t: [
            {
                "name": col["name"],
                "type": str(col["type"]),
                "nullable": col["nullable"]
            }
            for col in cols
        ]
        for t, cols in tables.items()
    }
    '''