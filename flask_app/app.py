from flask import Flask, render_template
import boto3
import pandas as pd
from pyspark.sql import SparkSession

app = Flask(__name__)


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

def get_apod_data():
    # Read processed Parquet data from LocalStack S3
    df = spark.read.parquet('s3a://apod-bucket/processed/')
    pandas_df = df.toPandas()  # Convert to Pandas for easy display
    return pandas_df

@app.route('/')
def index():
    apod_data = get_apod_data()
    return render_template('index.html', apod_data=apod_data)

if __name__ == '__main__':
    app.run(debug=True)
