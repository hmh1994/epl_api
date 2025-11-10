def map_row(row: dict, mapping: dict) -> dict:
    return {web_key: row.get(db_key) for db_key, web_key in mapping.items()}