import json
from pathlib import Path
import psycopg
from src.infra.db import get_dsn
from datetime import date


def load_rooms(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))

    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.executemany(
                """
                INSERT INTO rooms2 (id, name)
                VALUES (%s, %s)
                ON CONFLICT (id) DO NOTHING
                """,
                [(r["id"], r["name"]) for r in data]

            )


def load_students(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))

    rows = []
    for s in data:
        rows.append((
            s["id"],
            s["name"],
            s["birthday"],
            s["sex"],
            s["room"]
        ))

    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.executemany(
                """
                INSERT INTO students2 (id, name, birthday, sex, room_id)
                VALUES (%s, %s, %s::date, %s, %s)
                ON CONFLICT (id) DO NOTHING

                """,
                rows
            )


