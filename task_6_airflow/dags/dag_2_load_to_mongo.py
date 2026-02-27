from __future__ import annotations

import os
from datetime import datetime

import pandas as pd
from pymongo import MongoClient, UpdateOne

from airflow import DAG
from airflow.datasets import Dataset
from airflow.hooks.base import BaseHook
from airflow.operators.python import PythonOperator

# Must match DAG 1 output path so the scheduler links dataset updates to this DAG
OUTPUT_PATH = "/opt/airflow/data/processed/tiktok_reviews_processed.csv"
PROCESSED_DATASET = Dataset(f"file://{OUTPUT_PATH}")

# MongoDB connection
MONGO_CONN_ID = "mongo_local"
MONGO_DB = "airflow_task6"
MONGO_COLLECTION = "tiktok_reviews"


def load_csv_to_mongo(**context) -> None:
    """
    Read the processed CSV produced by DAG 1, normalize column names and types,
    then upsert each row into MongoDB using the Airflow Connection 'mongo_local'.
    """
    if not os.path.exists(OUTPUT_PATH):
        raise FileNotFoundError(f"Processed file not found: {OUTPUT_PATH}")

    df = pd.read_csv(OUTPUT_PATH)

    date_col = "created_date" if "created_date" in df.columns else ("at" if "at" in df.columns else None)
    if not date_col:
        raise ValueError("No date column found (expected 'created_date' or 'at').")

    content_col = "content"
    if content_col not in df.columns:
        raise ValueError("No 'content' column found.")

    rating_col = "rating" if "rating" in df.columns else ("score" if "score" in df.columns else None)

    df[date_col] = pd.to_datetime(df[date_col], errors="coerce", utc=True)
    if rating_col:
        df[rating_col] = pd.to_numeric(df[rating_col], errors="coerce")

    # Build MongoDB URI from Airflow Connection 
    conn = BaseHook.get_connection(MONGO_CONN_ID)
    login = conn.login or ""
    password = conn.password or ""
    host = conn.host or "mongo"
    port = conn.port or 27017
    schema = conn.schema or MONGO_DB

    if login and password:
        uri = f"mongodb://{login}:{password}@{host}:{port}/?authSource=admin"
    else:
        uri = f"mongodb://{host}:{port}"

    client = MongoClient(uri)
    db = client[schema]
    col = db[MONGO_COLLECTION]

    # Use reviewId as unique key for upsert when available; otherwise content + created_date
    id_col = "reviewId" if "reviewId" in df.columns else None

    ops = []
    for _, row in df.iterrows():
        doc = row.to_dict()

        if isinstance(doc.get(date_col), pd.Timestamp):
            doc[date_col] = doc[date_col].to_pydatetime()

        doc["created_date"] = doc.get("created_date") or doc.get("at")
        if isinstance(doc.get("created_date"), pd.Timestamp):
            doc["created_date"] = doc["created_date"].to_pydatetime()

        if "rating" not in doc and "score" in doc:
            doc["rating"] = doc["score"]

        if id_col:
            flt = {id_col: doc.get(id_col)}
        else:
            flt = {content_col: doc.get(content_col), "created_date": doc.get("created_date")}

        ops.append(UpdateOne(flt, {"$set": doc}, upsert=True))

    if ops:
        result = col.bulk_write(ops, ordered=False)
        context["ti"].log.info(
            "Mongo bulk_write done. matched=%s modified=%s upserted=%s",
            result.matched_count,
            result.modified_count,
            len(result.upserted_ids or {}),
        )

    client.close()

# DAG 2 runs when PROCESSED_DATASET is updated by DAG 1's last task.

with DAG(
    dag_id="dag_2_load_to_mongo",
    start_date=datetime(2025, 1, 1),
    schedule=[PROCESSED_DATASET],  # Data-aware scheduler creates a run when this dataset is updated
    catchup=False,
    tags=["task6", "mongo", "load"],
) as dag:
    load = PythonOperator(
        task_id="load_processed_csv_to_mongo",
        python_callable=load_csv_to_mongo,
    )