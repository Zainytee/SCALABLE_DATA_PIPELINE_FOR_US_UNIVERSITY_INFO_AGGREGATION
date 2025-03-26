# Overview

Welcome to Astronomer! This project was generated after you ran `astro dev init` using the Astronomer CLI. This README describes the contents of the project, how to run Apache Airflow on your local machine, and details our ETL process—including our custom data transformation using an AWS Lambda function.

# Project Contents

Your Astro project contains the following files and folders:

- **dags**: This folder contains the Python files for your Airflow DAGs. By default, this directory includes one example DAG:
  - `example_astronauts`: This DAG shows a simple ETL pipeline example that queries the list of astronauts currently in space from the Open Notify API and prints a statement for each astronaut. The DAG uses the TaskFlow API to define tasks in Python and dynamic task mapping to dynamically print a statement for each astronaut. For more on how this DAG works, see our [Getting Started Tutorial](https://www.astronomer.io/docs/learn/get-started-with-airflow).
- **Dockerfile**: Contains a versioned Astro Runtime Docker image that provides a differentiated Airflow experience. Use this file to execute other commands or overrides at runtime.
- **include**: This folder contains any additional files you want to include as part of your project. It is empty by default.
- **packages.txt**: Install OS-level packages needed for your project by adding them to this file. It is empty by default.
- **requirements.txt**: Install Python packages needed for your project by adding them to this file. It is empty by default.
- **plugins**: Add custom or community plugins for your project to this folder. It is empty by default.
- **airflow_settings.yaml**: Use this local-only file to specify Airflow Connections, Variables, and Pools instead of entering them in the Airflow UI as you develop DAGs in this project.

# Transformation Process Approach

In addition to our standard extraction and loading tasks, we have implemented a data transformation process using an AWS Lambda function. This process ensures that raw data is accurately transformed and enriched with custom ranking information before further processing.

**Steps:**

1. **Extraction:**
   - Raw JSON data is extracted from the College Scorecard API by an Airflow task.
   - The raw file is saved in a raw S3 bucket with a filename such as `college_data_YYYY-MM-DD.json`.

2. **Lambda Transformation:**
   - An S3 event notification triggers a Lambda function when a new raw file is uploaded.
   - The Lambda function:
     - Reads the raw JSON file from S3.
     - Transforms the data using Python and Pandas:
       - Extracts key fields (e.g., school name, location, tuition, admission rate, SAT/ACT scores).
       - Cleans the data by handling missing values and converting data types.
       - Computes a custom ranking score based on key metrics (Completion Rate, Average SAT, Retention Rate, Admission Rate, and In-State Tuition) using min–max normalization and weighted composite scoring.
     - Converts the transformed data into a CSV file.
     - Uploads the transformed CSV to a target S3 bucket (e.g., `transformed-college-data`) with a filename like `college_data_YYYY-MM-DD.csv`.

3. **Airflow Integration:**
   - An S3KeySensor task in Airflow monitors the target bucket to confirm the transformed file is available before downstream tasks continue.

# Deploy Your Project Locally

1. **Start Airflow on Your Local Machine:**
   - Run `astro dev start` to spin up Docker containers for:
     - Postgres (Airflow's metadata database)
     - Webserver (Airflow UI)
     - Scheduler (monitors and triggers tasks)
     - Triggerer (triggers deferred tasks)

2. **Verify Containers:**
   - Run `docker ps` to ensure all containers are running.
   - Note: The Airflow Webserver is exposed at port 8080 and Postgres at port 5432. Adjust if needed.

3. **Access the Airflow UI:**
   - Open [http://localhost:8080/](http://localhost:8080/) and log in with `admin` as both your username and password.
   - Your Postgres database is accessible at `localhost:5432/postgres`.

# Deploy Your Project to Astronomer

If you have an Astronomer account, pushing code to a Deployment on Astronomer is simple. For deployment instructions, refer to the [Astronomer documentation](https://www.astronomer.io/docs/astro/deploy-code/).

# Contact

The Astronomer CLI is maintained with love by the Astronomer team. To report a bug or suggest a change, please reach out to our support.
