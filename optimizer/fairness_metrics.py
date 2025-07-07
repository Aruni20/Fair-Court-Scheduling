# optimizer/fairness_metrics.py
"""
Compute fairness metrics for court scheduling.
Focuses on judge workload balance and fairness index.
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count, avg, stddev
from optimizer.utils import get_spark_session

def compute_fairness_metrics(scheduled_df):
    """Compute fairness metrics from scheduled cases."""
    try:
        spark = get_spark_session()
        
        workload = scheduled_df.groupBy("judge_id").agg(count("case_id").alias("case_count"))
        mean_workload = workload.agg(avg("case_count")).collect()[0][0]
        stddev_workload = workload.agg(stddev("case_count")).collect()[0][0]
        
        fairness_index = 1 - (stddev_workload / mean_workload if mean_workload > 0 else 0)
        print(f"Fairness Index: {fairness_index:.2f}")
        return {"fairness_index": fairness_index, "mean_workload": mean_workload}
    except Exception as e:
        print(f"Error computing fairness metrics: {e}")
        raise