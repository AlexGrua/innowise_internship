from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Any, Sequence

RowMapper = Callable[[dict[str, Any]], Sequence[Any]]

# Get project root directory
_PROJECT_ROOT = Path(__file__).resolve().parents[2]


@dataclass(frozen=True)
class LoadSpec:
    name: str
    table: str
    columns: list[str]
    source_path: str
    row_mapper: RowMapper
    conflict_columns: tuple[str, ...] = ("id",)


LOAD_SPECS: list[LoadSpec] = [
    LoadSpec(
        name="rooms",
        table="rooms2",
        columns=["id", "name"],
        source_path=str(_PROJECT_ROOT / "source" / "rooms.json"),
        row_mapper=lambda r: (r["id"], r["name"]),
    ),
    LoadSpec(
        name="students",
        table="students2",
        columns=["id", "name", "birthday", "sex", "room_id"],
        source_path=str(_PROJECT_ROOT / "source" / "students.json"),
        row_mapper=lambda s: (s["id"], s["name"], s["birthday"], s["sex"], s["room"]),
    ),
]
