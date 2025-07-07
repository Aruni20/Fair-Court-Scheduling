# analytics/extract_from_hdfs.py
"""
Extract historical and scheduled data from HDFS for analytics.
"""

from pyspark.sql import SparkSession
from config.config import HDFS_HOST, HDFS_HISTORICAL_PATH, HDFS_SCHEDULED_PATH

def extract_historical_data():
    """Extract historical case data from HDFS."""
    try:
        spark = SparkSession.builder \
            .appName("ExtractHistorical") \
            .config("spark.master", "spark://spark:7077") \
            .getOrCreate()
        
        df = spark.read.parquet(f"{HDFS_HOST}{HDFS_HISTORICAL_PATH}")
        print(f"Extracted historical data from {HDFS_HISTORICAL_PATH}")
        return df
    except Exception as e:
        print(f"Error extracting historical data: {e}")
        raise

def extract_scheduled_data(date_str):
    """Extract scheduled data for a specific date from HDFS."""
    try:
        spark = SparkSession.builder \
            .appName("ExtractScheduled") \
            .config("spark.master", "spark://spark:7077") \
            .getOrCreate()
        
        df = spark.read.parquet(f"{HDFS_HOST}{HDFS_SCHEDULED_PATH}/{date_str}")
        print(f"Extracted scheduled data from {HDFS_SCHEDULED_PATH}/{date_str}")
        return df
    except Exception as e:
        print(f"Error extracting scheduled data: {e}")
        raise