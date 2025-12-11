import json
import os
from datetime import datetime

import boto3
import requests
from botocore.exceptions import BotoCoreError, NoCredentialsError

LOCALSTACK_ENDPOINT = "http://localhost:4566"
BUCKET_NAME = "apod-bucket"

# LocalStack Configuration
localstack_s3 = boto3.client(
    "s3",
    endpoint_url=LOCALSTACK_ENDPOINT,
    aws_access_key_id="test",  # LocalStack default key
    aws_secret_access_key="test",  # LocalStack default secret
    region_name="us-east-1",
)

# NASA APOD API Configuration
nasa_api_key = os.getenv("NASA_API_KEY", "your-key-here")
api_url = f"https://api.nasa.gov/planetary/apod?api_key={nasa_api_key}&count=100"  # Fetch 100 random APOD items

def fetch_apod_data():
    if nasa_api_key == "your-key-here":
        print(
            "NASA_API_KEY is not set. Export your API key (e.g., export NASA_API_KEY=your_key) "
            "before running this script."
        )
        return

    try:
        response = requests.get(api_url)

        if response.status_code == 200:
            apod_data = response.json()

            # Filter out entries that are not images
            valid_images = [
                item for item in apod_data
                if item['media_type'] == 'image' and item['url'].lower().endswith(('.jpg', '.jpeg', '.png'))
            ]

            if not valid_images:
                print("No valid images found.")
                return

            file_name = f"apod_{datetime.now().strftime('%Y%m%d')}.json"

            # Save only valid image data locally
            with open(file_name, 'w') as file:
                json.dump(valid_images, file)

            # Upload JSON data to LocalStack S3
            try:
                localstack_s3.upload_file(file_name, BUCKET_NAME, f"raw/{file_name}")
                print(f"Data uploaded to s3://{BUCKET_NAME}/raw/{file_name}")
                os.remove(file_name)  # Clean up the local file after upload
            except NoCredentialsError:
                print("Credentials not available")
            except BotoCoreError as e:
                print(f"S3 Upload Error: {e}")
        else:
            print(f"Failed to fetch APOD data. Status code: {response.status_code}")
    except requests.RequestException as e:
        print(f"Error during API request: {e}")

fetch_apod_data()
