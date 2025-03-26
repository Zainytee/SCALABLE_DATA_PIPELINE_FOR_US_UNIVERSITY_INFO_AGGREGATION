from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime
import os
import json
import requests
import pandas as pd
import boto3
import clickhouse_connect

# Load environment variables
S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME", "my-tf-data-bucket-hackathon")
S3_OBJECT_NAME = "raw/all_college_data.json"

# Extract Data from API
def extract_data():
    API_KEY = os.getenv("COLLEGE_SCORECARD_API_KEY")
    URL = "https://api.data.gov/ed/collegescorecard/v1/schools.json"
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
    
    for page in range(1, 100):
        params["page"] = page
        response = requests.get(URL, params=params)
        if response.status_code != 200:
            raise Exception(f"Error on page {page}: {response.text}")
        
        results = response.json().get("results", [])
        if not results:
            break
        
        all_schools.extend(results)

    file_path = "/tmp/all_college_data.json"
    with open(file_path, "w") as file:
        json.dump(all_schools, file, indent=4)
    
    print("✅ Data extraction complete")

# Upload Extracted Data to S3
def upload_to_s3():
    file_path = "/tmp/all_college_data.json"
    s3_client = boto3.client("s3")
    
    try:
        s3_client.upload_file(file_path, S3_BUCKET_NAME, S3_OBJECT_NAME)
        print(f"✅ Uploaded to S3: s3://{S3_BUCKET_NAME}/{S3_OBJECT_NAME}")
    except Exception as e:
        print(f"Failed to upload to S3: {e}")
        raise

# Create ClickHouse Table
def create_clickhouse_table():
    client = clickhouse_connect.get_client(
        host=os.getenv("CLICKHOUSE_HOST", "clickhouse"),
        port=int(os.getenv("CLICKHOUSE_PORT", 8123)),
        username=os.getenv("CLICKHOUSE_USER", "admin"),
        password=os.getenv("CLICKHOUSE_PASSWORD", "mysecurepassword"),
    )

    create_table_sql = """
        CREATE TABLE IF NOT EXISTS college_data (
            id UInt32,
            name Nullable(String),
            city Nullable(String),
            state Nullable(String),
            address Nullable(String),
            admission_rate Nullable(Float32),
            act_score Nullable(UInt32),
            sat_score Nullable(UInt32),
            tuition_in_state Nullable(UInt32),
            tuition_out_state Nullable(UInt32),
            loan_principal Nullable(Float32),
            federal_loan_rate Nullable(Float32),
            completion_rate Nullable(Float32),
            student_size Nullable(UInt32),
            retention_rate Nullable(Float32),
            peps_ownership Nullable(String)
        ) ENGINE = MergeTree()
        ORDER BY id;
    """
    
    client.command(create_table_sql)
    print("✅ ClickHouse table created")

# Load Data into ClickHouse
def load_into_clickhouse():
    client = clickhouse_connect.get_client(
        host=os.getenv("CLICKHOUSE_HOST", "clickhouse"),
        port=int(os.getenv("CLICKHOUSE_PORT", 8123)),
        username=os.getenv("CLICKHOUSE_USER", "admin"),
        password=os.getenv("CLICKHOUSE_PASSWORD", "mysecurepassword"),
    )
    
    local_file = "/tmp/all_college_data.json"
    s3_client = boto3.client("s3")
    
    try:
        s3_client.download_file(S3_BUCKET_NAME, S3_OBJECT_NAME, local_file)
        print(f"✅ Downloaded from S3: {local_file}")
    except Exception as e:
        print(f"❌ Failed to download from S3: {e}")
        raise
    
    df = pd.read_json(local_file)
    
    # Rename the columns to match ClickHouse table schema
    df = df.rename(columns={
        "latest_admissions_admission_rate_overall": "admission_rate",
        "latest_admissions_act_scores_50th_percentile_cumulative": "act_score",
        "latest_admissions_sat_scores_average_overall": "sat_score",
        "latest_cost_tuition_in_state": "tuition_in_state",
        "latest_cost_tuition_out_of_state": "tuition_out_state",
        "latest_aid_loan_principal": "loan_principal",
        "latest_aid_federal_loan_rate": "federal_loan_rate",
        "latest_completion_4_yr_completion_overall": "completion_rate",
        "latest_student_size": "student_size",
        "latest_student_retention_rate_overall": "retention_rate",
        "latest_school_peps_ownership": "peps_ownership"
    })
    
    # Print the renamed columns to verify
    print("Renamed Columns:", df.columns.tolist())
    
    # Fill NaN values with empty strings and adjust column names
    df.fillna("", inplace=True)
    df.columns = [col.replace(".", "_") for col in df.columns]  # Ensure the column names match ClickHouse format
    formatted_data = df.to_numpy().tolist()
    column_names = df.columns.tolist()
    
    # Insert data into ClickHouse
    client.insert("college_data", formatted_data, column_names=column_names)
    print("✅ Data inserted into ClickHouse")

# Define the DAG
default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2025, 3, 25),
    "retries": 1,
}

with DAG(
    "api_to_s3_to_clickhouse",
    default_args=default_args,
    description="Extract data from API, upload to S3, and load into ClickHouse",
    schedule_interval="@daily",
) as dag:

    extract_task = PythonOperator(
        task_id="extract_data",
        python_callable=extract_data,
    )

    upload_task = PythonOperator(
        task_id="upload_to_s3",
        python_callable=upload_to_s3,
    )

    create_table_task = PythonOperator(
        task_id="create_clickhouse_table",
        python_callable=create_clickhouse_table,
    )

    load_task = PythonOperator(
        task_id="load_into_clickhouse",
        python_callable=load_into_clickhouse,
    )

    extract_task >> upload_task >> create_table_task >> load_task
