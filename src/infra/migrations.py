from pathlib import Path
import psycopg
from src.infra.db import get_dsn

def apply_schema():
    sql_path = Path(__file__).resolve().parents[2]/"schema.sql"
    sql = sql_path.read_text(encoding="utf-8")

    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute(sql)


def apply_indexes():
    sql_path = Path(__file__).resolve().parents[2]/"indexes.sql"
    sql = sql_path.read_text(encoding="utf-8")

    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute(sql)

