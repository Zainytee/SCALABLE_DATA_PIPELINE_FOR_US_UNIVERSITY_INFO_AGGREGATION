
# SCALABLE_DATA_PIPELINE_FOR_US_UNIVERSITY_INFO_AGGREGATION

## Introduction
The quest to gain knowledge and attend a good school has increased the demand for accurate and up-to-date information about colleges and universities in the United States. However, finding such information remains a major challenge for prospective students. With thousands of institutions nationwide, it becomes difficult to compare them based on key factors such as tuition fees, graduation rates, admission requirements, and available programs.

This project aims to solve this problem by building a scalable data pipeline that automates the extraction, transformation, and storage of university-related data from the College Scorecard API. The system retrieves information for the top 1000 schools in the U.S. based on rankings and organizes it in a structured format suitable for analytics and visualization. This enables students to make informed decisions using a data-driven approach.

![WhatsApp Image 2025-03-26 at 23 51 33](https://github.com/user-attachments/assets/8b3fcebe-eb88-4403-920e-9e72a28bfa5b)


## Implementation Details

### Data Extraction

The extraction process is implemented using Python, leveraging the requests library to pull data from the College Scorecard API. The extracted data includes school details, admission statistics, tuition costs, and performance metrics.
**Steps:**

1. **Extraction:**
   - Raw JSON data is extracted from the College Scorecard API by an Airflow task.
   - The raw file is saved in a raw S3 bucket with a filename such as `college_data_YYYY-MM-DD.json`.
  
### Data Storage & Transformation

Once extracted, the data is initially stored in an AWS S3 bucket. From there, an AWS Lambda function processes and transforms the raw data, handling inconsistencies and normalizing it for efficient analysis. The transformed data is then moved into ClickHouse, a high-performance columnar database optimized for analytical queries.
 **Lambda Transformation:**
   - An S3 event notification triggers a Lambda function when a new raw file is uploaded.
   - The Lambda function:
     - Reads the raw JSON file from S3.
     - Transforms the data using Python and Pandas:
       - Extracts key fields (e.g., school name, location, tuition, admission rate, SAT/ACT scores).
       - Cleans the data by handling missing values and converting data types.
       - Computes a custom ranking score based on key metrics (Completion Rate, Average SAT, Retention Rate, Admission Rate, and In-State Tuition) using min–max normalization and weighted composite scoring.
     - Converts the transformed data into a CSV file.
     - Uploads the transformed CSV to a target S3 bucket (e.g., `transformed-college-data`) with a filename like `college_data_YYYY-MM-DD.csv`.

### Pipeline Orchestration

The entire workflow is managed using Apache Airflow, ensuring automation, scheduling, and monitoring of data ingestion and transformation tasks. Airflow enables the system to scale efficiently while maintaining reliability.
 - An S3KeySensor task in Airflow monitors the target bucket to confirm the transformed file is available before downstream tasks continue.


### Data Accessibility & Visualization

To facilitate analysis and decision-making, the processed data is structured in a well-documented warehouse schema. This ensures ease of use for data analysts and developers working with the dataset. Additionally, dashboards were created using tools  Power BI to provide interactive visualizations of key university metrics and admission criteria.

### Error Handling & Monitoring

Comprehensive logging and error-handling mechanisms are in place to track API request failures, data inconsistencies, and processing issues. This ensures data integrity and reliability throughout the pipeline.

### Technology Stack

* Programming Language: Python

* API Access: Requests library

* Data Storage: AWS S3 (raw data), ClickHouse (structured storage)

* Data Processing: AWS Lambda (data transformation)

* Orchestration: Apache Airflow

* Visualization Tools: Power BI

### MetaData

<img width="727" alt="Screenshot 2025-03-26 at 21 34 19" src="https://github.com/user-attachments/assets/0938b38e-c66e-460a-aa3b-79727342b3a7" />

