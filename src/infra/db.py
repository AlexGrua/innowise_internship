import os
import psycopg
from dotenv import load_dotenv

load_dotenv(dotenv_path=".env")

def get_dsn() -> str:
    host = os.getenv("PG_HOST")
    port = os.getenv("PG_PORT")
    db = os.getenv("PG_DB")
    user = os.getenv("PG_USER")
    pwd = os.getenv("PG_PASSWORD")
    return f"postgresql://{user}:{pwd}@{host}:{port}/{db}"

def test_connection() -> None:
    with psycopg.connect(get_dsn()) as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT 1;")
            cur.fetchone()
