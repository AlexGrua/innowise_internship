import psycopg
from src.infra.db import get_dsn

def rooms_with_students_count():
    sql = """
    SELECT r.id, r.name, COUNT(s.id) as students_count
    FROM rooms2 r
    LEFT JOIN students2 s 
    ON s.room_id = r.id
    GROUP BY r.id, r.name
    ORDER BY r.id

    """

    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()

    return [
        {"id": rid, "name": name, "students_count": cnt}
        for (rid, name, cnt) in rows
    ]


def rooms_with_smallest_avg_age(limit: int = 5):
    sql = """
    SELECT r.id, r.name, 
            AVG(EXTRACT(YEAR FROM AGE(CURRENT_DATE, s.birthday))) as avg_age
    FROM rooms2 r
    JOIN students2 s 
    ON s.room_id = r.id
    GROUP BY r.id, r.name
    ORDER BY avg_age ASC
    LIMIT %s;
    """

    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (limit,))
            rows = cur.fetchall()
    return [

        {"id": rid, "name": name, "avg_age": float(avg_age)}
        for (rid, name, avg_age) in rows
    ]


def rooms_with_largest_age_diff(limit: int = 5):
    sql = """
    WITH t AS (
    SELECT r.id, r.name, 
        MIN(EXTRACT (YEAR FROM AGE (CURRENT_DATE, s.birthday))) as min_age,
        MAX(EXTRACT(YEAR FROM AGE(CURRENT_DATE, s.birthday))) as max_age
    FROM rooms2 r
    JOIN students2 s
    ON s.room_id = r.id
    GROUP BY r.id, r.name
    )
    SELECT id, name, (max_age - min_age) AS age_diff, min_age, max_age
    FROM t
    ORDER BY age_diff DESC
    LIMIT %s;
   
    """

    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute(sql, (limit,))
            rows = cur.fetchall()

    return [
        {"id": rid, "name": name, "age_diff":float(age_diff), "min_age": float(min_age), "max_age": float(max_age)}
        for (rid, name, age_diff, min_age, max_age) in rows
    ]

def rooms_with_mixed_sex():
    sql = """
    SELECT r.id, r.name, COUNT(DISTINCT s.sex) AS sex_count
    FROM rooms2 r
    JOIN students2 s
    ON r.id = s.room_id
    GROUP BY r.id, r.name
    HAVING COUNT(DISTINCT s.sex) = 2
    ORDER BY r.id
    """

    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
            rows = cur.fetchall()

    return [
        {"id": rid, "name": name}
        for (rid, name, _) in rows
    ]


def build_report():
    return{
        "rooms_with_students_count": rooms_with_students_count(),
        "rooms_with_smallest_avg_age": rooms_with_smallest_avg_age(),
        "rooms_with_largest_age_diff": rooms_with_largest_age_diff(),
        "rooms_with_mixed_sex": rooms_with_mixed_sex(),
    }
