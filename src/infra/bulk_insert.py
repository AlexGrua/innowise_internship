from __future__ import annotations

from typing import Iterable, Sequence, Any, Optional
import psycopg

from src.infra.db import get_dsn


def bulk_insert(
    table: str,
    columns: Sequence[str],
    rows: Iterable[Sequence[Any]],
    conflict_columns: Sequence[str] = ("id",),
) -> None:
    cols = ", ".join(columns)
    placeholders = ", ".join(["%s"] * len(columns))

    conflict = ", ".join(conflict_columns)
    sql = f"""
    INSERT INTO {table} ({cols})
    VALUES ({placeholders})
    ON CONFLICT ({conflict}) DO NOTHING
    """

    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.executemany(sql, list(rows))
