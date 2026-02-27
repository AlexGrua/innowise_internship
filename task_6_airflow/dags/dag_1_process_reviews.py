from __future__ import annotations

import os
import re
from datetime import datetime

import pandas as pd

from airflow import DAG
from airflow.datasets import Dataset
from airflow.operators.bash import BashOperator
from airflow.operators.empty import EmptyOperator
from airflow.operators.python import BranchPythonOperator, PythonOperator
from airflow.sensors.python import PythonSensor
from airflow.utils.task_group import TaskGroup


INCOMING_DIR = "/opt/airflow/data/incoming"
PROCESSED_DIR = "/opt/airflow/data/processed"

INPUT_FILENAME = "tiktok_google_play_reviews.csv"
INPUT_PATH = os.path.join(INCOMING_DIR, INPUT_FILENAME)

OUTPUT_FILENAME = "tiktok_reviews_processed.csv"
OUTPUT_PATH = os.path.join(PROCESSED_DIR, OUTPUT_FILENAME)

# Dataset for DAG2 
PROCESSED_DATASET = Dataset(f"file://{OUTPUT_PATH}")


def _is_file_empty(path: str) -> bool:
    """
    Return True if the file is empty: missing, 0 bytes, or only header (no data rows).
    Used by the branch to decide between 'empty_file_log' and 'transformations' path.
    """
    if not os.path.exists(path):
        return True
    if os.path.getsize(path) == 0:
        return True

    with open(path, "r", encoding="utf-8", errors="ignore") as f:
        lines = [ln.strip() for ln in f.readlines() if ln.strip()]

    # 0 lines is empty file; 1 line is header only, no data rows
    return len(lines) <= 1


def branch_on_empty(**context) -> str:
    """
    BranchPythonOperator callable: returns the task_id of the next task to run.
    """
    return "empty_file_log" if _is_file_empty(INPUT_PATH) else "transformations.start"


def replace_nulls_callable(**context) -> None:
    """
    Transformation 1: Replace all 'null' (string, any case) and NaN with '-'.
    Reads from INPUT_PATH, writes to a temporary file for the next step.
    """
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    df = pd.read_csv(INPUT_PATH)

    df = df.replace(to_replace=r"(?i)^null$", value="-", regex=True)
    df = df.fillna("-")

    tmp_path = os.path.join(PROCESSED_DIR, "_tmp_step1.csv")
    df.to_csv(tmp_path, index=False)


def sort_by_created_date_callable(**context) -> None:
    """
    Transformation 2: Sort rows by created_date (column 'at' in source CSV).
    Reads from step 1 temp file, writes to step 2 temp file.
    """
    tmp_in = os.path.join(PROCESSED_DIR, "_tmp_step1.csv")
    df = pd.read_csv(tmp_in)

    if "at" not in df.columns:
        raise ValueError("Column 'at' not found in CSV (expected review timestamp).")

    df["at"] = pd.to_datetime(df["at"], errors="coerce", utc=True)
    df = df.sort_values(by="at", ascending=True)

    tmp_out = os.path.join(PROCESSED_DIR, "_tmp_step2.csv")
    df.to_csv(tmp_out, index=False)


# Regex: remove any character that is NOT alphanumeric (EN + RU), whitespace, or common punctuation.
# Effect: strips emojis, symbols, etc., leaving only text and punctuation.
_ALLOWED_TEXT_RE = re.compile(r"[^0-9A-Za-zА-Яа-яЁё\s\.\,\!\?\:\;\'\"\-\(\)\[\]\{\}]", re.UNICODE)


def clean_content_callable(**context) -> None:
    """
    Transformation 3: Clean the 'content' column (remove emojis/symbols, keep text and punctuation),
    normalize column names for MongoDB queries (created_date, rating), write final CSV.
    This task has outlets=[PROCESSED_DATASET]; on success, DAG 2 will be triggered.
    """
    tmp_in = os.path.join(PROCESSED_DIR, "_tmp_step2.csv")
    df = pd.read_csv(tmp_in)

    if "content" not in df.columns:
        raise ValueError("Column 'content' not found in CSV.")

    if "created_date" not in df.columns and "at" in df.columns:
        df["created_date"] = df["at"]
    if "rating" not in df.columns and "score" in df.columns:
        df["rating"] = df["score"]

    def clean_text(x):
        if pd.isna(x):
            return "-"
        s = str(x)
        s = _ALLOWED_TEXT_RE.sub("", s)
        s = re.sub(r"\s+", " ", s).strip()
        return s if s else "-"

    df["content"] = df["content"].apply(clean_text)

    os.makedirs(PROCESSED_DIR, exist_ok=True)
    df.to_csv(OUTPUT_PATH, index=False)

    for p in [
        os.path.join(PROCESSED_DIR, "_tmp_step1.csv"),
        os.path.join(PROCESSED_DIR, "_tmp_step2.csv"),
    ]:
        try:
            os.remove(p)
        except FileNotFoundError:
            pass


# DAG 1: manual trigger only (schedule=None); data flow via Dataset to DAG 2

with DAG(
    dag_id="dag_1_process_reviews",
    start_date=datetime(2025, 1, 1),
    schedule=None, 
    catchup=False,
    tags=["task6", "processing"],
) as dag:
    # Sensor: poll until INPUT_PATH exists (file dropped into incoming folder). Blocks for up to 1 hour.
    wait_for_file = PythonSensor(
        task_id="wait_for_file",
        python_callable=lambda: os.path.exists(INPUT_PATH),
        poke_interval=10,
        timeout=60 * 60,
        mode="poke",
    )

    # Branch: decide next task by file content (empty vs has data). Returns task_id string.
    branch = BranchPythonOperator(
        task_id="branch_on_empty",
        python_callable=branch_on_empty,
    )

    empty_file_log = BashOperator(
        task_id="empty_file_log",
        bash_command=f'echo "File is empty: {INPUT_PATH}"',
    )

    # Common sink for both branches so the DAG run completes cleanly.
    done = EmptyOperator(task_id="done")

    # TaskGroup: three sequential transformations; only one branch runs this.
    with TaskGroup(group_id="transformations") as transformations:
        start = EmptyOperator(task_id="start")

        t1_replace_nulls = PythonOperator(
            task_id="replace_nulls",
            python_callable=replace_nulls_callable,
        )

        t2_sort_by_date = PythonOperator(
            task_id="sort_by_created_date",
            python_callable=sort_by_created_date_callable,
        )

        # Last step writes OUTPUT_PATH and triggers DAG 2 via data-aware scheduling
        t3_clean_content = PythonOperator(
            task_id="clean_content_and_write_final",
            python_callable=clean_content_callable,
            outlets=[PROCESSED_DATASET],
        )

        start >> t1_replace_nulls >> t2_sort_by_date >> t3_clean_content

    wait_for_file >> branch
    branch >> empty_file_log >> done
    branch >> transformations >> done