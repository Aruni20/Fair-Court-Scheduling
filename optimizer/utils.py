# optimizer/utils.py
"""
Utility functions for the optimizer pipeline.
Handles HDFS data loading and judge availability checks.
"""

from pyspark.sql import SparkSession
import mysql.connector
from config.config import HDFS_HOST

def get_spark_session():
    """Create and return a Spark session."""
    try:
        spark = SparkSession.builder \
            .appName("CourtScheduling") \
            .config("spark.master", "spark://spark:7077") \
            .getOrCreate()
        return spark
    except Exception as e:
        print(f"Error creating Spark session: {e}")
        raise

def load_from_hdfs(path):
    """Load JSON data from HDFS into a Spark DataFrame."""
    try:
        spark = get_spark_session()
        df = spark.read.json(f"{HDFS_HOST}{path}")
        return df
    except Exception as e:
        print(f"Error loading data from HDFS {path}: {e}")
        raise

def check_judge_availability(judge_id, scheduled_date):
    """Check if judge is available on the given date."""
    try:
        conn = mysql.connector.connect(
            host="mysql",
            user="airflow",
            password="airflow",
            database="court_db"
        )
        cursor = conn.cursor()
        
        cursor.execute("SELECT holiday_date FROM Court_Holidays WHERE holiday_date = %s", (scheduled_date,))
        if cursor.fetchone():
            return False
        
        cursor.execute("SELECT leave_date FROM Judge_Leave WHERE judge_id = %s AND leave_date = %s", 
                      (judge_id, scheduled_date))
        if cursor.fetchone():
            return False
            
        cursor.close()
        conn.close()
        return True
    except Exception as e:
        print(f"Error checking judge availability: {e}")
        raise