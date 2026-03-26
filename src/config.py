"""Centralized configuration for the Big Data Fraud pipeline."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# === Paths ===
PROJECT_ROOT = Path(__file__).parent.parent
DATA_RAW = PROJECT_ROOT / os.getenv("DATA_RAW_PATH", "data/raw")
DATA_DELTA = PROJECT_ROOT / os.getenv("DATA_DELTA_PATH", "data/delta")
BRONZE_PATH = str(DATA_DELTA / "bronze" / "transactions")
SILVER_PATH = str(DATA_DELTA / "silver" / "transactions")
GOLD_PATH = str(DATA_DELTA / "gold" / "fraud_metrics")

# === Spark Config ===
SPARK_APP_NAME = "bigdata-fraud-pyspark"
SPARK_DRIVER_MEMORY = os.getenv("SPARK_DRIVER_MEMORY", "8g")
SPARK_EXECUTOR_MEMORY = os.getenv("SPARK_EXECUTOR_MEMORY", "4g")

# === Data Generation ===
DEFAULT_NUM_RECORDS = 100_000_000
FRAUD_RATIO = 0.012  # ~1.2% fraud rate (realistic)
SEED = 42

# === Partitioning ===
PARTITION_COLS_BRONZE = ["year", "month"]
PARTITION_COLS_SILVER = ["year", "month", "is_fraud"]
NUM_BUCKETS = 64
BUCKET_COL = "account_id"
