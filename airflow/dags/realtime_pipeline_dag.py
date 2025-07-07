# airflow/dags/realtime_pipeline_dag.py
"""
Airflow DAG for real-time court scheduling pipeline.
Runs every 5 minutes to process new cases, optimize schedules, and upload reports to website.
"""

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from optimizer.scoring import compute_priority_scores
from optimizer.scheduler import schedule_cases
from reporting.generate_html import generate_schedule_html, upload_to_web_server
from feedback_loop.store_to_hdfs import store_schedules_to_hdfs
from config.config import AIRFLOW_DAG_DEFAULT_ARGS
import mysql.connector

default_args = AIRFLOW_DAG_DEFAULT_ARGS

with DAG(
    'realtime_court_scheduling',
    default_args=default_args,
    description='Real-time court scheduling pipeline',
    schedule_interval=timedelta(minutes=5),
    start_date=datetime(2025, 7, 7),
    catchup=False
) as dag:
    
    def extract_and_score():
        """Extract from HDFS and compute priority scores."""
        from optimizer.utils import load_from_hdfs
        date_str = datetime.now().strftime("%Y/%m/%d")
        df = load_from_hdfs(f"/live/{date_str}")
        scored_df = compute_priority_scores(df)
        return scored_df
    
    def optimize_schedules():
        """Run greedy scheduling algorithm."""
        scored_df = extract_and_score()
        scheduled_df = schedule_cases(scored_df)
        return scheduled_df
    
    def generate_and_upload_reports():
        """Generate HTML reports and upload to web server."""
        scheduled_df = optimize_schedules()
        output_path = f"/data/schedule_{datetime.now().strftime('%Y-%m-%d')}.html"
        html_content, date_str = generate_schedule_html(scheduled_df.collect(), output_path)
        url = upload_to_web_server(output_path, date_str)
        print(f"Schedule available at {url}")
        return scheduled_df
    
    def store_results():
        """Store schedules to HDFS."""
        scheduled_df = generate_and_upload_reports()
        date_str = datetime.now().strftime("%Y/%m/%d")
        store_schedules_to_hdfs(scheduled_df, date_str)
    
    def update_outcomes():
        """Update Schedule_Log outcomes in MySQL (placeholder)."""
        try:
            conn = mysql.connector.connect(
                host="mysql",
                user="airflow",
                password="airflow",
                database="court_db"
            )
            cursor = conn.cursor()
            cursor.execute("UPDATE Schedule_Log SET outcome = 'Scheduled' WHERE outcome IS NULL")
            conn.commit()
            cursor.close()
            conn.close()
            print("Updated Schedule_Log outcomes")
        except Exception as e:
            print(f"Error updating outcomes: {e}")
            raise
    
    task_extract_score = PythonOperator(
        task_id='extract_and_score',
        python_callable=extract_and_score
    )
    
    task_optimize = PythonOperator(
        task_id='optimize_schedules',
        python_callable=optimize_schedules
    )
    
    task_report = PythonOperator(
        task_id='generate_and_upload_reports',
        python_callable=generate_and_upload_reports
    )
    
    task_store = PythonOperator(
        task_id='store_results',
        python_callable=store_results
    )
    
    task_update_outcomes = PythonOperator(
        task_id='update_outcomes',
        python_callable=update_outcomes
    )
    
    task_extract_score >> task_optimize >> task_report >> task_store >> task_update_outcomes