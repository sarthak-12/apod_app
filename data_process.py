from pyspark.sql import SparkSession
from pyspark.sql.functions import col

# Initialize Spark session with S3A configurations
# Initialize Spark session with S3A configurations
spark = SparkSession.builder \
    .appName('APODDataProcessing') \
    .config("spark.hadoop.fs.s3a.access.key", "test") \
    .config("spark.hadoop.fs.s3a.secret.key", "test") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://localhost:4566") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false") \
    .getOrCreate()

# Read APOD data from LocalStack S3
def process_apod_data():
    s3_url = 's3a://apod-bucket/raw/apod_*.json'  # Read all APOD data from the S3 bucket
    df = spark.read.json(s3_url)

    # Select relevant columns
    processed_df = df.select(
        col('date').alias('apod_date'),
        col('title').alias('apod_title'),
        col('url').alias('image_url'),
        col('explanation').alias('description')
    )

    # Write processed data back to LocalStack S3
    processed_df.write.parquet('s3a://apod-bucket/processed/', mode='overwrite')
    print("Data processed and saved to LocalStack S3")

process_apod_data()
