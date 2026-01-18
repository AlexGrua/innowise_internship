from pathlib import Path

from src.infra.sql_runner import run_sql


def apply_schema() -> None:
    sql_path = Path(__file__).resolve().parents[2] / "sql" / "schema.sql"
    run_sql(sql_path)


def apply_indexes() -> None:
    sql_path = Path(__file__).resolve().parents[2] / "sql" / "indexes.sql"
    run_sql(sql_path)

