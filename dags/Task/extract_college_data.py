import os
import requests
import json
from airflow.models import Variable
from datetime import datetime

# Define an output directory (relative to this file) to store the raw data
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), 'data')
os.makedirs(OUTPUT_DIR, exist_ok=True)

def extract_college_data(**kwargs):
    # Get the API key from an Airflow Variable (set this in the Airflow UI)
    api_key = Variable.get("college_scorecard_api_key")
    
    # Define the base URL and fields for extraction
    base_url = "https://api.data.gov/ed/collegescorecard/v1/schools"
    fields = (
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
    
    # Build query parameters. You can pass optional kwargs like 'page' and 'per_page'
    query_params = {
        "api_key": api_key,
        "per_page": kwargs.get("per_page", 100),
        "page": kwargs.get("page", 1),
        "fields": fields
    }
    
    # Create a datetime string to timestamp your output file
    dt_string = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    
    try:
        response = requests.get(base_url, params=query_params)
        response.raise_for_status()
        data = response.json()
        
        # Save the raw JSON data to a file in the output directory
        output_file = os.path.join(OUTPUT_DIR, f"college_data_{dt_string}.json")
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=4)
        
        print(f"Data saved locally to: {output_file}")
        return output_file
        
    except requests.exceptions.RequestException as e:
        print(f"Error making API request: {e}")
        raise
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON response: {e}")
        raise
