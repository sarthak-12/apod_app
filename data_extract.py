import requests
import json
import boto3
from datetime import datetime
from botocore.exceptions import NoCredentialsError

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
api_url = f'https://api.nasa.gov/planetary/apod?api_key={nasa_api_key}&count=5'  # Fetch 5 random APOD images

def fetch_apod_data():
    response = requests.get(api_url)
    apod_data = response.json()
    file_name = f'apod_{datetime.now().strftime("%Y%m%d")}.json'

    # Save APOD data locally
    with open(file_name, 'w') as file:
        json.dump(apod_data, file)

    # Upload JSON data to LocalStack S3
    try:
        localstack_s3.upload_file(file_name, bucket_name, f'raw/{file_name}')
        print(f'Data uploaded to s3://{bucket_name}/raw/{file_name}')
    except NoCredentialsError:
        print("Credentials not available")

fetch_apod_data()
