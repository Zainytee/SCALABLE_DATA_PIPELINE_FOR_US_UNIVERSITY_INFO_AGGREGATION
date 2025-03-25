from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import os
import clickhouse_connect

def insert_into_clickhouse():
    client = clickhouse_connect.get_client(
        host=os.getenv("CLICKHOUSE_HOST", "clickhouse"),
        port=int(os.getenv("CLICKHOUSE_PORT", 8123)),
        username=os.getenv("CLICKHOUSE_USER", "admin"),
        password=os.getenv("CLICKHOUSE_PASSWORD", "mysecurepassword")
    )

    client.command("""
        CREATE TABLE IF NOT EXISTS new_table (
            key UInt32,
            value String,
            metric Float32
        ) ENGINE = MergeTree()
        ORDER BY key;
    """)
    
    data = [
        [1000, 'String Value 1000', 5.233],
        [2000, 'String Value 2000', -107.04]
    ]
    client.insert('new_table', data, column_names=['key', 'value', 'metric'])
    print("Data inserted successfully!")

dag = DAG(
    'clickhouse_insert_dag',
    default_args={'owner': 'airflow', 'start_date': datetime(2024, 3, 25)},
    schedule_interval=None,
)

insert_task = PythonOperator(
    task_id='insert_into_clickhouse',
    python_callable=insert_into_clickhouse,
    dag=dag,
)

insert_task
