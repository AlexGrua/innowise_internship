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

SQL Architecture

All analytical SQL queries are stored in a single file:
sql/queries.sql

Each query is identified by a named marker:
```bash
-- name: rooms_with_students_count
SELECT ...
```

## Data Loading Architecture

Data loading is declarative and configuration-driven

Sources, tables, columns, and mappings are defined in:
```bash
src/config/load_registry.py
```

The loader is universal:

no hardcoded load_rooms / load_students

adding a new table requires only a new config entry

Current data sources:

source/rooms.json

source/students.json

## Environment Configuration

Database connection settings are shown in a `.env.example` file 

## Usage

- Initialize database schema and indexes:
```bash
python -m src.main --format json --init-db
```
- Load data only (without building reports)

Useful for initial data import or reloading source files.

```bash
python -m src.main --format json --load-only
```

- Generate reports in JSON format:

```bash
python -m src.main --format json
```

- Generate reports in XML format:
```bash
python -m src.main --format xml
```

- Run a single report

Executes only one specific analytical query.

```bash
python -m src.main --format json --report rooms_with_smallest_avg_age
```

- Available report names:

rooms_with_students_count

rooms_with_smallest_avg_age

rooms_with_largest_age_diff

rooms_with_mixed_sex


- Limit the number of results

Applies to reports that support top-N semantics (average age, age difference).

```bash
python -m src.main --format json --report rooms_with_smallest_avg_age --limit 10
```

```bash
python -m src.main --format json --report rooms_with_largest_age_diff --limit 3
```

- Combined example

Initialize database, load data, and run a single report with custom limit:
```bash
python -m src.main --format json --init-db --report rooms_with_largest_age_diff --limit 5
```


## Output

The result is printed to `stdout` in JSON or XML format depending on the `--format` argument.

The output structure depends on the selected execution mode:

### Full report output
When no specific report is selected, all analytical reports are executed and returned:

```json
{
  "rooms_with_students_count": [...],
  "rooms_with_smallest_avg_age": [...],
  "rooms_with_largest_age_diff": [...],
  "rooms_with_mixed_sex": [...]
}
```

### Single report output

When a specific report is selected using --report, only that report is returned,
while preserving the same dictionary-based structure:

```json
{
  "rooms_with_smallest_avg_age": [...]
}
```

---

## Docker Usage

- Build and start PostgreSQL + run full report
```bash
docker compose up --build
```
- Run a single report (example: smallest average age, limit 3)

```bash
docker compose run --rm app \
  python -m src.main --format json \
  --report rooms_with_smallest_avg_age \
  --limit 3
```

- Load
```bash
docker compose run --rm app \
  python -m src.main --load-only
```


## Key Points

- PostgreSQL is used as the relational database  
- Many-to-one relationship between students and rooms  
- Pure SQL queries, no ORM  
- All calculations are done in the database  
- Indexes are added for query optimization  
- Fully configurable CLI interface:

  --selective report execution;

  --configurable result limits;
  
  --load-only and init-db modes;

- Designed for reproducibility and containerization (Docker-ready)
