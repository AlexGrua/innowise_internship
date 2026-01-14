# Rooms & Students — PostgreSQL + Python CLI

This project is a Python CLI application that loads data from two JSON files (`rooms.json`, `students.json`) into a PostgreSQL database and generates analytical reports using pure SQL.

All calculations are performed at the database level. Python is used only for data loading, orchestration, and output serialization. The solution follows OOP and SOLID principles and does not use any ORM.

---

## Data Model

- rooms(id, name)
- students(id, name, birthday, sex, room_id)

Relationship: many students belong to one room.

---

## Reports

The application generates the following reports using SQL:

1. List of rooms and number of students in each room  
2. Top 5 rooms with the smallest average student age  
3. Top 5 rooms with the largest age difference  
4. Rooms where students of different sexes live  

All age calculations are done in PostgreSQL.

---

## Environment Configuration

Database connection settings are stored in a `.env` file (not committed to git)

## Usage

Initialize database schema and indexes:
```bash
python -m src.main --rooms rooms.json --students students.json --format json --init-db
```

Generate reports in JSON format:

```bash
python -m src.main --rooms rooms.json --students students.json --format json
```

Generate reports in XML format:
```bash
python -m src.main --rooms rooms.json --students students.json --format xml
```

## Output

The result is printed to stdout in JSON or XML format depending on the `--format` argument.

---

## Key Points

- PostgreSQL is used as the relational database  
- Many-to-one relationship between students and rooms  
- Pure SQL queries, no ORM  
- All calculations are done in the database  
- Indexes are added for query optimization  
- CLI-based execution with configurable input paths  
