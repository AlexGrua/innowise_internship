from __future__ import annotations

from pathlib import Path
from typing import Iterable, Optional, Sequence, Any

import psycopg

from src.infra.db import get_dsn


def run_sql(sql: str, params: Optional[Sequence[Any]] = None) -> None:

    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            if params is None:
                cur.execute(sql)
            else:
                cur.execute(sql, params)


def run_sql_file(path: Path) -> None:

    sql = path.read_text(encoding="utf-8")
    run_sql(sql)


def fetch_all(sql: str, params: Optional[Sequence[Any]] = None) -> list[tuple]:

    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            if params is None:
                cur.execute(sql)
            else:
                cur.execute(sql, params)
            return cur.fetchall()