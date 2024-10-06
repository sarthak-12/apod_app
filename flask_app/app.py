from flask import Flask, render_template
import boto3
import pandas as pd
from pyspark.sql import SparkSession
import random
import os

app = Flask(__name__)

# Initialize Spark Session to read from LocalStack S3
spark = SparkSession.builder \
    .appName("APODDataProcessing") \
    .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.4,com.amazonaws:aws-java-sdk-bundle:1.12.262") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .config("spark.hadoop.fs.s3a.access.key", "test") \
    .config("spark.hadoop.fs.s3a.secret.key", "test") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://localhost:4566") \
    .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false") \
    .getOrCreate()

# Connect to LocalStack S3
s3 = boto3.client('s3', endpoint_url='http://localhost:4566')

def get_latest_parquet_folder():
    # List directories in the "processed" bucket to find the latest folder
    response = s3.list_objects_v2(Bucket='apod-bucket', Prefix='processed/', Delimiter='/')
    if 'CommonPrefixes' in response:
        folders = [prefix['Prefix'] for prefix in response['CommonPrefixes']]
        latest_folder = max(folders)  # Find the latest timestamped folder
        return latest_folder
    return None

def get_apod_data():
    # Get the latest Parquet folder path
    latest_folder = get_latest_parquet_folder()
    
    if latest_folder is None:
        return pd.DataFrame()  # Return an empty DataFrame if no folder is found

    # Read processed Parquet data from LocalStack S3
    s3_path = f's3a://apod-bucket/{latest_folder}'
    print(f"Reading data from: {s3_path}")
    
    try:
        df = spark.read.parquet(s3_path)
        pandas_df = df.toPandas()  # Convert to Pandas for easy display
        
        # Randomly select 5 images from the dataset
        if len(pandas_df) >= 5:
            random_apod_data = pandas_df.sample(5)  # Select 5 random rows
        else:
            random_apod_data = pandas_df  # If less than 5 entries, use all available
        
        return random_apod_data

    except Exception as e:
        print(f"Error reading Parquet data: {e}")
        return pd.DataFrame()  # Return an empty DataFrame in case of error

@app.route('/')
def index():
    apod_data = get_apod_data()
    return render_template('index.html', apod_data=apod_data)

if __name__ == '__main__':
    app.run(debug=True)
