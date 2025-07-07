# optimizer/scheduler.py
"""
Greedy scheduling algorithm to assign cases to courtrooms and judges.
Ensures no overlaps and balances workloads.
"""

from pyspark.sql import SparkSession
from datetime import datetime, time, timedelta
import mysql.connector
from config.config import MYSQL_CONN
from optimizer.utils import check_judge_availability, get_spark_session

def schedule_cases(scored_df):
    """Schedule cases based on priority scores."""
    try:
        spark = get_spark_session()
        conn = mysql.connector.connect(
            host="mysql",
            user="airflow",
            password="airflow",
            database="court_db"
        )
        cursor = conn.cursor()
        
        # Get available courts and judges
        cursor.execute("SELECT court_id FROM Court")
        courts = [row[0] for row in cursor.fetchall()]
        cursor.execute("SELECT judge_id FROM Judge")
        judges = [row[0] for row in cursor.fetchall()]
        
        # Initialize schedule
        scheduled_cases = []
        current_date = datetime.now().date()
        time_blocks = [time(hour=h) for h in range(9, 17)]  # 9 AM to 5 PM
        judge_workload = {judge: 0 for judge in judges}
        
        # Convert DataFrame to list
        cases = scored_df.collect()
        
        for case in cases:
            case_id = case['case_id']
            duration = case['estimated_duration_blocks']
            priority = case['priority_score']
            
            # Find compatible judge and court
            for judge_id in judges:
                if not check_judge_availability(judge_id, current_date):
                    continue
                
                for court_id in courts:
                    for start_time in time_blocks:
                        end_time = (datetime.combine(current_date, start_time) + 
                                   timedelta(hours=duration)).time()
                        if end_time.hour > 17:
                            continue
                        
                        # Check for overlaps
                        overlap = any(
                            s['court_id'] == court_id and 
                            s['scheduled_date'] == current_date and
                            not (s['end_time'] <= start_time or end_time <= s['start_time'])
                            for s in scheduled_cases
                        )
                        if overlap:
                            continue
                        
                        # Assign case
                        scheduled_cases.append({
                            'case_id': case_id,
                            'judge_id': judge_id,
                            'court_id': court_id,
                            'scheduled_date': current_date,
                            'start_time': start_time,
                            'end_time': end_time,
                            'outcome': None,
                            'created_at': datetime.now()
                        })
                        judge_workload[judge_id] += duration
                        break
                    if any(s['case_id'] == case_id for s in scheduled_cases):
                        break
                if any(s['case_id'] == case_id for s in scheduled_cases):
                    break
        
        # Convert to DataFrame
        scheduled_df = spark.createDataFrame(scheduled_cases)
        print(f"Judge workloads: {judge_workload}")
        
        # Insert schedules into MySQL Schedule_Log
        for schedule in scheduled_cases:
            cursor.execute("""
                INSERT INTO Schedule_Log (case_id, judge_id, court_id, scheduled_date, 
                                         start_time, end_time, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                schedule['case_id'], schedule['judge_id'], schedule['court_id'],
                schedule['scheduled_date'], schedule['start_time'], schedule['end_time'],
                schedule['created_at']
            ))
        conn.commit()
        
        cursor.close()
        conn.close()
        return scheduled_df
    except Exception as e:
        print(f"Error scheduling cases: {e}")
        raise