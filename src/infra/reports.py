from __future__ import annotations

from pathlib import Path
from typing import Any, Sequence

from src.infra.sql_runner import fetch_all

DEFAULT_LIMIT = 5

QUERIES_FILE = Path("sql/queries.sql")


def _load_named_queries(sql_file: Path = QUERIES_FILE) -> dict[str, str]:
    text = sql_file.read_text(encoding="utf-8")
    queries: dict[str, str] = {}

    current_name: str | None = None
    buf: list[str] = []

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("-- name:"):
            # save previous block
            if current_name is not None:
                queries[current_name] = "\n".join(buf).strip()
                buf.clear()

            current_name = stripped.split(":", 1)[1].strip()
            continue

        if current_name is not None:
            buf.append(line)

    # save last block
    if current_name is not None:
        queries[current_name] = "\n".join(buf).strip()

    return queries


def run_analytical_query(query_name: str, params: Sequence[Any] | None = None):
    queries = _load_named_queries()
    if query_name not in queries:
        raise KeyError(f"Unknown query_name='{query_name}'. Available: {sorted(queries.keys())}")
    return fetch_all(queries[query_name], params)


def build_report():
    return {
        "rooms_with_students_count": [
            {"id": r[0], "name": r[1], "students_count": r[2]}
            for r in run_analytical_query("rooms_with_students_count")
        ],
        "rooms_with_smallest_avg_age": [
            {"id": r[0], "name": r[1], "avg_age": float(r[2])}
            for r in run_analytical_query("rooms_with_smallest_avg_age", params=(DEFAULT_LIMIT,))
        ],
        "rooms_with_largest_age_diff": [
            {
                "id": r[0],
                "name": r[1],
                "age_diff": float(r[2]),
                "min_age": float(r[3]),
                "max_age": float(r[4]),
            }
            for r in run_analytical_query("rooms_with_largest_age_diff", params=(DEFAULT_LIMIT,))
        ],
        "rooms_with_mixed_sex": [
            {"id": r[0], "name": r[1]}
            for r in run_analytical_query("rooms_with_mixed_sex")
        ],
    }
