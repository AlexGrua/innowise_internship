from __future__ import annotations

from pathlib import Path
from os import PathLike
from typing import Optional, Sequence, Any, Union

import psycopg
from src.infra.db import get_dsn

SqlInput = Union[str, PathLike]


def run_sql(sql: SqlInput, params: Optional[Sequence[Any]] = None) -> None:
    """
    Execute a SQL statement that does not return any result.

    Accepts either a raw SQL string or a filesystem path to a .sql file.
    Intended for DDL and non-SELECT queries (schema, indexes, inserts).
    Used primarily for database migrations (schema and indexes).
    """
    if not isinstance(sql, str):
        sql = Path(sql).read_text(encoding="utf-8")

    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())


def fetch_all(sql: str, params: Optional[Sequence[Any]] = None) -> list[tuple]:
    """
    Execute a SELECT query and return all result rows.
    Used for analytical queries in reports.
    """
    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, params or ())
            return cur.fetchall()
