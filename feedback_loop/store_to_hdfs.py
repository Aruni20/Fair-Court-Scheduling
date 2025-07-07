# feedback_loop/store_to_hdfs.py
"""
Store optimized schedules to HDFS /scheduled/ and /historical/ for analytics.
"""

from pyspark.sql import SparkSession
from config.config import HDFS_HOST, HDFS_SCHEDULED_PATH, HDFS_HISTORICAL_PATH
from datetime import datetime

def store_schedules_to_hdfs(df, date_str):
    """Store schedules DataFrame to HDFS as Parquet."""
    try:
        spark = SparkSession.builder \
            .appName("StoreSchedules") \
            .config("spark.master", "spark://spark:7077") \
            .getOrCreate()
        
        scheduled_path = f"{HDFS_HOST}{HDFS_SCHEDULED_PATH}/{date_str}"
        df.write.mode("overwrite").parquet(scheduled_path)
        print(f"Saved schedules to {scheduled_path}")
        
        historical_path = f"{HDFS_HOST}{HDFS_HISTORICAL_PATH}"
        df.write.mode("append").parquet(historical_path)
        print(f"Appended schedules to {historical_path}")
        
        spark.stop()
    except Exception as e:
        print(f"Error storing schedules to HDFS: {e}")
        raise