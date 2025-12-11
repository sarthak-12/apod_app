# NASA APOD Local Pipeline

A tiny data pipeline that fetches NASA Astronomy Picture of the Day (APOD) entries, stages them in a LocalStack S3 bucket, curates them with PySpark, and serves a dashboard with Flask.

![NASA APOD Dashboard](docs/assets/nasa-apod-dashboard.svg)

## Why this exists
- **Sandboxed cloud feel:** Use LocalStack to practice S3-based data flows without touching real AWS.
- **ETL in miniature:** Extract JSON from the NASA API, transform it to a tidy Parquet dataset, and write it back.
- **Visual payoff:** A lightweight dashboard showcases random APOD images from the processed data.

## Architecture
1. **data_extract.py** — Pulls APOD entries from the NASA API, filters for images, and uploads a dated JSON file to `s3://apod-bucket/raw/` on LocalStack.
2. **data_process.py** — Uses PySpark to read all raw JSON files, select the key fields (date, title, url, explanation), and write a timestamped Parquet folder to `s3://apod-bucket/processed/`.
3. **flask_app/app.py** — Reads the most recent Parquet folder, converts it to Pandas, samples five rows, and renders them as flip cards in the dashboard.

## Prerequisites
- Python 3.9+
- LocalStack running with S3 on `http://localhost:4566`
- AWS-style credentials that match the defaults used by LocalStack: `AWS_ACCESS_KEY_ID=test` and `AWS_SECRET_ACCESS_KEY=test`
- A NASA API key (free at https://api.nasa.gov) exported as `NASA_API_KEY`

Create and activate a virtual environment to avoid the PEP 668 "externally-managed" error:
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running the pipeline
1. **Create the S3 bucket on LocalStack**
   - With `awslocal` (awscli-local):
     ```bash
     awslocal s3 mb s3://apod-bucket
     ```
   - With the standard AWS CLI pointed at LocalStack:
     ```bash
     aws --endpoint-url http://localhost:4566 s3 mb s3://apod-bucket
     ```

2. **Extract raw APOD data**
   ```bash
   export NASA_API_KEY=your_api_key
   python data_extract.py
   ```

3. **Process to Parquet**
   ```bash
   python data_process.py
   ```

4. **Launch the dashboard**
   ```bash
   python flask_app/app.py
   # or
   FLASK_APP=flask_app/app.py flask run
   ```
   Open http://localhost:5000 to see a fresh set of APOD cards.

## Tips
- Re-running steps 2 and 3 will append new dated files; the Flask app automatically uses the most recent processed folder.
- If LocalStack is down, S3 operations will fail—start it before running the scripts.
- Adjust endpoints and credentials in the scripts if your LocalStack settings differ.
