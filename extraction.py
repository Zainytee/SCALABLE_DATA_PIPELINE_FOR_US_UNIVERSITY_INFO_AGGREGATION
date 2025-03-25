import os
import requests
import json
import logging
import time
import boto3

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s: %(message)s",
    handlers=[
        logging.FileHandler("college_scorecard_pipeline.log"),
        logging.StreamHandler()
    ]
)

API_KEY = "AGGv1ovetThDwRy2CIUQr9Izdsous9B1WZFifhfb"
BASE_URL = "https://api.data.gov/ed/collegescorecard/v1/schools"
FIELDS = (
    "id,school.name,school.city,school.state,school.ownership,"
    "latest.student.size,latest.admissions.admission_rate.overall,"
    "latest.admissions.sat_scores.average.overall,"
    "latest.admissions.act_scores.midpoint.cumulative,"
    "latest.cost.tuition.in_state,latest.cost.tuition.out_of_state,"
    "latest.cost.financial_aid,"
    "latest.cost.average_net_price.public,latest.cost.average_net_price.private,"
    "latest.completion.rate_4yr_150nt,"
    "latest.student.retention_rate,"
    "latest.earnings.10_yrs_after_entry.median,"
    "latest.earnings.6_yrs_after_entry.median"
)

def fetch_data(page: int = 0, per_page: int = 100, max_retries: int = 3) -> dict:
    params = {
        "api_key": API_KEY,
        "page": page,
        "per_page": per_page,
        "fields": FIELDS
    }
    retries = 0
    backoff = 2  # seconds
    while retries < max_retries:
        try:
            response = requests.get(BASE_URL, params=params)
            response.raise_for_status()
            logging.info("Fetched page %d successfully.", page)
            return response.json()
        except requests.exceptions.RequestException as e:
            retries += 1
            logging.error("API request failed on page %d (attempt %d/%d): %s", page, retries, max_retries, e)
            if retries < max_retries:
                time.sleep(backoff)
                backoff *= 2
            else:
                logging.error("Max retries reached for page %d. Skipping this page.", page)
                return {}

def main():
    total_records = []
    pages = 10
    for page in range(1, pages + 1):
        api_data = fetch_data(page=page, per_page=100)
        records = api_data.get("results", [])
        if records:
            total_records.extend(records)
        else:
            logging.error("No records returned for page %d", page)
    
    if not total_records:
        logging.error("No data extracted from the API. Exiting.")
        return
    
    file_name = "all_college_data.json"
    with open(file_name, "w") as file:
        json.dump(total_records, file, indent=4)
    logging.info("Saved %d colleges to %s", len(total_records), file_name)
    
    s3_bucket = "my-tf-data-bucket-hackathon20"  # Adjust to your bucket name
    s3_object = "raw/all_college_data.json"
    s3_client = boto3.client("s3")
    try:
        s3_client.upload_file(file_name, s3_bucket, s3_object)
        logging.info("File uploaded to s3://%s/%s", s3_bucket, s3_object)
    except Exception as e:
        logging.error("Failed to upload to S3: %s", e)
    print("Extraction complete.")

if __name__ == "__main__":
    main()
