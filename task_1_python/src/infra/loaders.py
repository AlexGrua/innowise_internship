from __future__ import annotations

from src.config.load_registry import LOAD_SPECS
from src.infra.load_from_json import load_json_into_table


def load_all_sources() -> None:
    """
    Load all configured source files into the database.

    Iterates over LoadSpec definitions and performs bulk inserts
    for each declared table.
    """
    
    for spec in LOAD_SPECS:
        load_json_into_table(
            path=spec.source_path,
            table=spec.table,
            columns=spec.columns,
            row_mapper=spec.row_mapper,
            conflict_columns=spec.conflict_columns,
        )