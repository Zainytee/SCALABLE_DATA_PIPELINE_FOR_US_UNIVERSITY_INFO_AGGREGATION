import requests
import json

# API details
URL = "https://api.data.gov/ed/collegescorecard/v1/schools.json"
API_KEY = "G6OLu9FgUvL3GNn9sokkiMuTEIM8ubr5DPY6YT10"


# Required fields
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

# API request parameters
params = {"api_key": API_KEY, "_fields": FIELDS, "per_page": 100}

all_schools = []  # Store all records

# Use a for loop with a high upper limit, stopping when no more results
for page in range(1, 1000):  # Arbitrary large number
    params["page"] = page
    response = requests.get(URL, params=params)

    if response.status_code != 200:
        print(f"Error on page {page}: {response.text}")
        break

    results = response.json().get("results", [])
    if not results:
        break  # Stop when no more data

    all_schools.extend(results)
    print(f"Fetched {len(results)} records from page {page}")

# Save data to JSON file
file_name = "all_college_data.json"
with open(file_name, "w") as file:
    json.dump(all_schools, file, indent=4)

print(f"Saved {len(all_schools)} colleges to all_college_data.json")


