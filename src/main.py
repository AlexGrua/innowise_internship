import argparse
from src.infra.db import test_connection
from src.infra.migrations import apply_indexes, apply_schema
from src.infra.loaders import load_rooms, load_students
from src.infra.reports import rooms_with_students_count, rooms_with_smallest_avg_age
from src.infra.reports import rooms_with_largest_age_diff, rooms_with_mixed_sex, build_report
from src.infra.serializers import serialize_json, serialize_xml


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--students", required=True)
    p.add_argument("--rooms", required=True)
    p.add_argument("--format", required=True, choices=["json", "xml"])
    p.add_argument("--init-db", action="store_true")
    return p.parse_args()

def main():
    args = parse_args()
    test_connection()


    if args.init_db:
        apply_schema()
        apply_indexes()
        print("Schema and Indexes applied")

    
    load_rooms(args.rooms)
    print("Rooms loaded")

    load_students(args.students)
    print("Students loaded")

    report = build_report()

    if args.format == "json":
        print(serialize_json(report))
    elif args.format == "xml":
        print(serialize_xml(report))


if __name__ == "__main__":
    main()


