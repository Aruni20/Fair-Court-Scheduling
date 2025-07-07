# analytics/load_to_clickhouse.py
"""
Load computed KPIs, schedules, and case data into ClickHouse for analytics dashboard.
"""

from clickhouse_driver import Client
from config.config import CLICKHOUSE_HOST, CLICKHOUSE_DB

def load_kpis_to_clickhouse(kpis, date_str, schedules_df, cases_df):
    """Load KPIs, schedules, and cases into ClickHouse."""
    try:
        client = Client(host=CLICKHOUSE_HOST, database=CLICKHOUSE_DB)
        
        # Create KPI table
        client.execute("""
        CREATE TABLE IF NOT EXISTS kpi_metrics (
            date String,
            fairness_index Float32,
            undertrial_percentage Float32,
            avg_delay_days Float32,
            adjournment_rate Float32
        ) ENGINE = MergeTree() ORDER BY date
        """)
        
        # Insert KPIs
        client.execute(
            "INSERT INTO kpi_metrics (date, fairness_index, undertrial_percentage, avg_delay_days, adjournment_rate) VALUES",
            [(date_str, kpis["fairness_index"], kpis["undertrial_percentage"], kpis["avg_delay_days"], kpis["adjournment_rate"])]
        )
        
        # Create Schedules table
        client.execute("""
        CREATE TABLE IF NOT EXISTS schedules (
            schedule_id UInt32,
            case_id String,
            judge_id UInt32,
            court_id UInt32,
            scheduled_date Date,
            start_time String,
            end_time String,
            outcome Nullable(String),
            created_at DateTime
        ) ENGINE = MergeTree() ORDER BY scheduled_date
        """)
        
        # Insert schedules
        schedules_data = [
            (
                row.get('schedule_id', 0), row.case_id, row.judge_id, row.court_id,
                row.scheduled_date, str(row.start_time), str(row.end_time), row.outcome,
                row.created_at
            )
            for row in schedules_df.collect()
        ]
        client.execute("INSERT INTO schedules VALUES", schedules_data)
        
        # Create Cases table
        client.execute("""
        CREATE TABLE IF NOT EXISTS cases (
            case_id String,
            case_number String,
            filing_date Date,
            case_type_id UInt32,
            court_id UInt32,
            is_undertrial Bool,
            vulnerability_index Float32,
            urgency_score Float32,
            status String,
            estimated_duration_blocks UInt8
        ) ENGINE = MergeTree() ORDER BY filing_date
        """)
        
        # Insert cases
        cases_data = [
            (
                row.case_id, row.case_number, row.filing_date, row.case_type_id,
                row.court_id, row.is_undertrial, row.vulnerability_index,
                row.urgency_score, row.status, row.estimated_duration_blocks
            )
            for row in cases_df.collect()
        ]
        client.execute("INSERT INTO cases VALUES", cases_data)
        
        print(f"Loaded KPIs, schedules, and cases for {date_str} into ClickHouse")
    except Exception as e:
        print(f"Error loading to ClickHouse: {e}")
        raise