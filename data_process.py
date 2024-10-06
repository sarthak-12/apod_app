from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pyspark.sql.types import StructType, StructField, StringType
from datetime import datetime
from botocore.exceptions import BotoCoreError

# Initialize Spark session with S3A configurations
spark = SparkSession.builder \
    .appName('APODDataProcessing') \
    .config("spark.hadoop.fs.s3a.access.key", "test") \
    .config("spark.hadoop.fs.s3a.secret.key", "test") \
    .config("spark.hadoop.fs.s3a.endpoint", "http://localhost:4566") \
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
    .config("spark.hadoop.fs.s3a.path.style.access", "true") \
    .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false") \
    .config("spark.sql.parquet.mergeSchema", "false") \
    .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.1,com.amazonaws:aws-java-sdk-bundle:1.12.262") \
    .getOrCreate()

# Define the schema for the JSON files
schema = StructType([
    StructField("date", StringType(), True),
    StructField("title", StringType(), True),
    StructField("url", StringType(), True),
    StructField("explanation", StringType(), True)
])

# Read and process APOD data from LocalStack S3
def process_apod_data():
    try:
        # Define the S3 path (wildcard to load multiple JSON files)
        s3_url = 's3a://apod-bucket/raw/apod_*.json'  # Wildcard to read multiple APOD JSON files
        print(f"Reading data from {s3_url}")
        
        # Read JSON files from S3 using the defined schema
        df = spark.read.schema(schema).json(s3_url)

        if df.count() == 0:
            print("No data found in the specified S3 location.")
            return
        
        print(f"Loaded {df.count()} records from S3.")

        # Select relevant columns from the dataframe
        processed_df = df.select(
            col('date').alias('apod_date'),
            col('title').alias('apod_title'),
            col('url').alias('image_url'),
            col('explanation').alias('description')
        )

        # Ensure processed folder structure and filenames avoid collisions
        output_path = f's3a://apod-bucket/processed/{datetime.now().strftime("%Y%m%d_%H%M%S")}/'
        print(f"Writing processed data to {output_path}")
        
        # Write the processed data to LocalStack S3 as Parquet
        processed_df.write.mode('overwrite').parquet(output_path)

        print("Data successfully processed and saved to LocalStack S3.")

    except BotoCoreError as e:
        print(f"S3-related error: {e}")
    except Exception as e:
        print(f"Error processing APOD data: {e}")

# Call the processing function
process_apod_data()
