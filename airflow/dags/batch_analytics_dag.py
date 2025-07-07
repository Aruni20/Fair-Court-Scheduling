# airflow/dags/batch_analytics_dag.py
"""
Airflow DAG for batch analytics pipeline.
Runs nightly to compute KPIs and update ClickHouse.
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from analytics.extract_from_hdfs import extract_historical_data, extract_scheduled_data
from analytics.compute_kpis import compute_kpis
from analytics.load_to_clickhouse import load_kpis_to_clickhouse
from config.config import AIRFLOW_DAG_DEFAULT_ARGS

default_args = AIRFLOW_DAG_DEFAULT_ARGS

with DAG(
    'batch_court_analytics',
    default_args=default_args,
    description='Batch analytics pipeline for KPIs',
    schedule_interval='@daily',
    start_date=datetime(2025, 7, 7),
    catchup=False
) as dag:
    
    def run_analytics():
        """Extract data, compute KPIs, and load to ClickHouse."""
        date_str = datetime.now().strftime("%Y/%m/%d")
        historical_df = extract_historical_data()
        scheduled_df = extract_scheduled_data(date_str)
        kpis = compute_kpis(historical_df, scheduled_df)
        load_kpis_to_clickhouse(kpis, datetime.now().strftime("%Y-%m-%d"), scheduled_df, historical_df)
    
    task_analytics = PythonOperator(
        task_id='run_analytics',
        python_callable=run_analytics
    )
    
    task_analytics