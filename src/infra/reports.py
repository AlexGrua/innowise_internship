from __future__ import annotations

from pathlib import Path
from typing import Any, Sequence

from src.infra.sql_runner import fetch_all

QUERIES_FILE = Path("sql/queries.sql")
DEFAULT_LIMIT = 5


def _load_named_queries(sql_file: Path = QUERIES_FILE) -> dict[str, str]:
    """
    Parse a SQL file and extract named SQL queries into a dictionary.
    The file must contain blocks marked with '-- name: <query_name>'.
    Each block is collected and mapped as {query_name: sql_text}.
    """
    text = sql_file.read_text(encoding="utf-8")
    queries: dict[str, str] = {}

    current_name: str | None = None
    buf: list[str] = []

    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("-- name:"):
            if current_name is not None:
                queries[current_name] = "\n".join(buf).strip()
                buf.clear()
            current_name = stripped.split(":", 1)[1].strip()
            continue

        if current_name is not None:
            buf.append(line)

    if current_name is not None:
        queries[current_name] = "\n".join(buf).strip()

    return queries


def run_analytical_query(query_name: str, params: Sequence[Any] | None = None) -> list[tuple]:
    """
    Execute a named analytical SQL query and return all result rows.
    Loads SQL from the shared queries file, executes the selected query,
    and returns raw database rows.
    Used for analytical queries in reports.
    """
    queries = _load_named_queries()
    if query_name not in queries:
        raise KeyError(f"Unknown query_name='{query_name}'. Available: {sorted(queries.keys())}")
    return fetch_all(queries[query_name], params)


def build_report(limit: int = DEFAULT_LIMIT, only: str | None = None) -> dict:
    """
    Builds the final analytical report.

    Executes one or all analytical queries depending on CLI arguments,
    applies limits where applicable, and aggregates results
    into a single dictionary ready for serialization
    """
    def run(name: str, params: Sequence[Any] | None = None) -> list[tuple]:
        return run_analytical_query(name, params)

    report_builders: dict[str, Any] = {
        "rooms_with_students_count": lambda: [
            {"id": r[0], "name": r[1], "students_count": r[2]}
            for r in run("rooms_with_students_count")
        ],
        "rooms_with_smallest_avg_age": lambda: [
            {"id": r[0], "name": r[1], "avg_age": float(r[2])}
            for r in run("rooms_with_smallest_avg_age", (limit,))
        ],
        "rooms_with_largest_age_diff": lambda: [
            {
                "id": r[0],
                "name": r[1],
                "age_diff": float(r[2]),
                "min_age": float(r[3]),
                "max_age": float(r[4]),
            }
            for r in run("rooms_with_largest_age_diff", (limit,))
        ],
        "rooms_with_mixed_sex": lambda: [
            {"id": r[0], "name": r[1]}
            for r in run("rooms_with_mixed_sex")
        ],
    }

    # If a specific report is requested via CLI (--report),
    # build and return only that report.
    if only is not None:
        if only not in report_builders:
            raise KeyError(f"Unknown report='{only}'. Available: {sorted(report_builders.keys())}")
        return {only: report_builders[only]()} 

    # Otherwise, build and return all available reports.
    return {name: builder() for name, builder in report_builders.items()}
