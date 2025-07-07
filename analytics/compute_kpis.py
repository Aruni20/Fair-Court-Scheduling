# analytics/compute_kpis.py
"""
Compute KPIs for analytics pipeline (fairness, undertrials, delays, adjournments).
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, avg, count, datediff, stddev
from datetime import datetime, timedelta

def compute_kpis(historical_df, scheduled_df):
    """Compute KPIs from historical and scheduled data."""
    try:
        spark = SparkSession.builder \
            .appName("ComputeKPIs") \
            .config("spark.master", "spark://spark:7077") \
            .getOrCreate()
        
        # Fairness Index
        workload = scheduled_df.groupBy("judge_id").agg(count("case_id").alias("case_count"))
        mean_workload = workload.agg(avg("case_count")).collect()[0][0] or 1
        stddev_workload = workload.agg(stddev("case_count")).collect()[0][0] or 0
        fairness_index = 1 - (stddev_workload / mean_workload)
        
        # Undertrials within 7 days
        undertrial_df = scheduled_df.join(historical_df, "case_id") \
            .filter(col("is_undertrial") == True) \
            .filter(datediff(col("scheduled_date"), col("filing_date")) <= 7)
        undertrial_count = undertrial_df.count()
        total_undertrial = historical_df.filter(col("is_undertrial") == True).count()
        undertrial_percentage = (undertrial_count / total_undertrial * 100) if total_undertrial > 0 else 0
        
        # Average delay
        avg_delay = historical_df.join(scheduled_df, "case_id") \
            .select(avg(datediff(col("scheduled_date"), col("filing_date")))
                   .alias("avg_delay")).collect()[0]["avg_delay"] or 0
        
        # Adjournment rate
        adjournment_count = scheduled_df.filter(col("outcome") == "Adjourned").count()
        total_schedules = scheduled_df.count()
        adjournment_rate = (adjournment_count / total_schedules * 100) if total_schedules > 0 else 0
        
        kpis = {
            "fairness_index": float(fairness_index),
            "undertrial_percentage": float(undertrial_percentage),
            "avg_delay_days": float(avg_delay),
            "adjournment_rate": float(adjournment_rate)
        }
        
        print(f"Computed KPIs: {kpis}")
        return kpis
    except Exception as e:
        print(f"Error computing KPIs: {e}")
        raise