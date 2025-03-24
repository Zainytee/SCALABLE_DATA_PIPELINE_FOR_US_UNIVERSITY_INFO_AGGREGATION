import boto3
# AWS S3 Details
S3_BUCKET_NAME = "my-tf-data-bucket-hackathon"
S3_OBJECT_NAME = "raw/all_college_data.json"  # File path in S3


# Initialize S3 client
s3_client = boto3.client("s3")

file_name = "all_college_data.json"

# Upload JSON file to S3
try:
    s3_client.upload_file(file_name, S3_BUCKET_NAME, S3_OBJECT_NAME)
    print(f"File uploaded to s3://{S3_BUCKET_NAME}/{S3_OBJECT_NAME}")
except Exception as e:
    print(f"Failed to upload to S3: {e}")