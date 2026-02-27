FROM apache/airflow:2.8.4-python3.11

USER airflow
RUN pip install --no-cache-dir \
    "pymongo" \
    "apache-airflow-providers-mongo" \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-2.8.4/constraints-3.11.txt" \
    --no-deps