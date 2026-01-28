from __future__ import annotations

import json
from pathlib import Path
from typing import Callable, Any, Sequence

from src.infra.bulk_insert import bulk_insert


RowMapper = Callable[[dict[str, Any]], Sequence[Any]]


def load_json_into_table(
    path: str | Path,
    table: str,
    columns: list[str],
    row_mapper: RowMapper,
    conflict_columns: tuple[str, ...] = ("id",),
) -> None:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    rows = (row_mapper(obj) for obj in data)
    bulk_insert(table=table, columns=columns, rows=rows, conflict_columns=conflict_columns)
