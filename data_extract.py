import requests
import json
import boto3
from datetime import datetime
import os
from botocore.exceptions import NoCredentialsError, BotoCoreError

# LocalStack Configuration
localstack_s3 = boto3.client(
    's3',
    endpoint_url='http://localhost:4566',
    aws_access_key_id='test',  # LocalStack default key
    aws_secret_access_key='test',  # LocalStack default secret
    region_name='us-east-1'
)
bucket_name = 'apod-bucket'

# NASA APOD API Configuration
nasa_api_key = 'yBYI28eM78itihb0vV0ewYtZdhgNmjYKaDHr2tia'
api_url = f'https://api.nasa.gov/planetary/apod?api_key={nasa_api_key}&count=100'  # Fetch 100 random APOD items

def fetch_apod_data():
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

            file_name = f'apod_{datetime.now().strftime("%Y%m%d")}.json'

            # Save only valid image data locally
            with open(file_name, 'w') as file:
                json.dump(valid_images, file)

            # Upload JSON data to LocalStack S3
            try:
                localstack_s3.upload_file(file_name, bucket_name, f'raw/{file_name}')
                print(f'Data uploaded to s3://{bucket_name}/raw/{file_name}')
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
