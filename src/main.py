import argparse

from src.infra.db import test_connection
from src.infra.migrations import apply_indexes, apply_schema
from src.infra.loaders import load_all_sources
from src.infra.reports import build_report
from src.infra.serializers import serialize_json, serialize_xml


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--format", required=True, choices=["json", "xml"])
    p.add_argument("--init-db", action="store_true")
    p.add_argument("--load-only", action="store_true", help="Only load sources into DB, do not build reports")
    p.add_argument("--limit", type=int, default=5, help="Limit for top-N reports (e.g. avg age, age diff)")
    p.add_argument("--report", type=str, default=None, help="Run a single report by name")
    return p.parse_args()


def main():
    args = parse_args()

    test_connection()

    if args.init_db:
        apply_schema()
        apply_indexes()
        print("Schema and Indexes applied")

    load_all_sources()
    print("Sources loaded")

    if args.load_only:
        return

    report = build_report(limit=args.limit, only=args.report)

    if args.format == "json":
        print(serialize_json(report))
    else:
        print(serialize_xml(report))


if __name__ == "__main__":
    main()
