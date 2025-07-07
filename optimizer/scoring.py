# optimizer/scoring.py
"""
Compute priority scores for cases based on undertrial status, vulnerability,
last hearing gap, and urgency score.
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from config.config import SCORING_WEIGHTS
from optimizer.utils import get_spark_session

def compute_priority_scores(df):
    """Compute priority scores for cases in the DataFrame."""
    try:
        spark = get_spark_session()
        
        required_columns = ['case_id', 'is_undertrial', 'vulnerability_index', 
                          'last_hearing_gap_days', 'urgency_score']
        if not all(col in df.columns for col in required_columns):
            raise ValueError("Missing required columns in DataFrame")
        
        # Compute priority_score = α·uᵢ + β·(1 - vᵢ) + γ·(1 / (gᵢ + 1)) + δ·tᵢ
        df_scored = df.withColumn(
            "priority_score",
            (SCORING_WEIGHTS['alpha'] * col("is_undertrial").cast("int")) +
            (SCORING_WEIGHTS['beta'] * (1 - col("vulnerability_index"))) +
            (SCORING_WEIGHTS['gamma'] * (1 / (col("last_hearing_gap_days") + 1))) +
            (SCORING_WEIGHTS['delta'] * col("urgency_score"))
        )
        
        df_scored = df_scored.orderBy(col("priority_score").desc())
        print("Computed priority scores for cases")
        return df_scored
    except Exception as e:
        print(f"Error computing priority scores: {e}")
        raise