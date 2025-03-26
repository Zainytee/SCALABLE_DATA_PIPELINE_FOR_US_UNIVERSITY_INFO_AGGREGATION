import os
import boto3
import logging
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta
from Task.extract_college_data import extract_college_data
from airflow.providers.amazon.aws.transfers.local_to_s3 import LocalFilesystemToS3Operator
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor

# Configure logging (Airflow also handles logging, so this is optional)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s"
)


default_args = {
    'owner': 'Abdulwajeed',
    'depends_on_past': False,
    'start_date': datetime(2024, 12, 25),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(seconds=5),
}

dag = DAG('college_data_extraction', default_args=default_args, schedule_interval='@daily', catchup=False)

extract_task = PythonOperator(
    task_id='extract_college_data',
    python_callable=extract_college_data,
    op_kwargs={'page': 1, 'per_page': 100},
    dag=dag
)

load_to_s3 = LocalFilesystemToS3Operator(
    task_id='Load_to_s3',
    filename='{{ task_instance.xcom_pull(task_ids="extract_college_data") }}',
    dest_key='raw/college_data_{{ ds }}.json',
    dest_bucket='my-tf-data-bucket-hackathon20',
    replace=True,
    aws_conn_id='aws_default',
    dag=dag
)

''''check_s3_file = S3KeySensor(
    task_id='check_transformed_data',
    bucket_name='transformed-college-data',
    bucket_key='college_data_{{ ds }}.csv',
    aws_conn_id='aws_default',
    poke_interval=60,
    timeout=3600,
    mode='poke',
    dag=dag)'''

extract_task >> load_to_s3 #>> #check_s3_file
