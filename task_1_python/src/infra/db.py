from __future__ import annotations
from contextlib import contextmanager
from pathlib import Path

import os
from typing import Sequence, Any, Optional, Iterator

import psycopg
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")


def get_dsn() -> str:
    host = os.getenv("PG_HOST")
    port = os.getenv("PG_PORT")
    db = os.getenv("PG_DB")
    user = os.getenv("PG_USER")
    pwd = os.getenv("PG_PASSWORD")
    return f"postgresql://{user}:{pwd}@{host}:{port}/{db}"


@contextmanager
def get_cursor() -> Iterator[psycopg.Cursor]:
    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            yield cur


def execute(sql: str, params: Optional[Sequence[Any]] = None) -> list[tuple]:
    """
    Execute a SQL statement and return all result rows.
    For DDL and non-SELECT queries, returns an empty list.
    For SELECT queries, returns the result rows.
    """
    with get_cursor() as cur:
        cur.execute(sql, params or ())
        if cur.description is not None:
            return cur.fetchall()
        return []


def test_connection() -> None:
    with get_cursor() as cur:
        cur.execute("SELECT 1;")
        cur.fetchone()


def apply_sql_file(filename: str) -> None:
    """Apply a SQL file from the sql directory."""
    sql_path = Path(__file__).resolve().parents[2] / "sql" / filename
    sql = sql_path.read_text(encoding="utf-8")
    execute(sql)
