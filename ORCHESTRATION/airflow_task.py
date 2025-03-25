from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import requests
import json
import boto3
from dotenv import load_dotenv
import os

load_dotenv()


# Extraction Function
def extract_data():
    URL = "https://api.data.gov/ed/collegescorecard/v1/schools.json"
    API_KEY = os.getenv("COLLEGE_SCORECARD_API_KEY")
    FIELDS = (
        "id,school.name,school.city,school.state,school.address,"
        "latest.admissions.admission_rate.overall,"
        "latest.admissions.act_scores.50th_percentile.cumulative,"
        "latest.admissions.sat_scores.average.overall,"
        "latest.cost.tuition.in_state,"
        "latest.cost.tuition.out_of_state,"
        "latest.aid.loan_principal,"
        "latest.aid.federal_loan_rate,"
        "latest.completion.4_yr_completion.overall,"
        "latest.student.size,"
        "latest.student.retention_rate.overall,"
        "latest.school.peps_ownership"
    )

    params = {"api_key": API_KEY, "_fields": FIELDS, "per_page": 100}
    all_schools = []

    for page in range(1, 1000):
        params["page"] = page
        response = requests.get(URL, params=params)
        if response.status_code != 200:
            raise Exception(f"Error on page {page}: {response.text}")
        results = response.json().get("results", [])
        if not results:
            break
        all_schools.extend(results)

    file_name = "/tmp/all_college_data.json"
    with open(file_name, "w") as file:
        json.dump(all_schools, file, indent=4)


# Loading Function
def load_to_s3():
    S3_BUCKET_NAME = "my-tf-data-bucket-hackathon"
    S3_OBJECT_NAME = "raw/all_college_data.json"
    file_name = "/tmp/all_college_data.json"

    # Initialize S3 client
    s3_client = boto3.client("s3")

    # Upload JSON file to S3 with error handling
    try:
        s3_client.upload_file(file_name, S3_BUCKET_NAME, S3_OBJECT_NAME)
        print(f"File uploaded to s3://{S3_BUCKET_NAME}/{S3_OBJECT_NAME}")
    except Exception as e:
        print(f"Failed to upload to S3: {e}")


# Define the DAG
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2025, 3, 25),
    "retries": 1,
}

with DAG(
    "data_extraction_and_s3_upload",
    default_args=default_args,
    description="Extract data from API and upload to S3",
    schedule_interval="@daily",  # Schedule to run daily
) as dag:

    extract_task = PythonOperator(
        task_id="extract_data",
        python_callable=extract_data,
    )

    load_task = PythonOperator(
        task_id="load_to_s3",
        python_callable=load_to_s3,
    )

    extract_task >> load_task  # Task dependency
