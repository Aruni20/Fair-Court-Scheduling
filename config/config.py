# config/config.py
"""
Configuration file for court scheduling pipeline.
Contains database connections, Kafka topics, HDFS paths, and scoring weights.
"""

# Kafka settings
KAFKA_BOOTSTRAP_SERVERS = 'kafka:9092'
KAFKA_TOPIC_CASES = 'cases_real_time'

# HDFS settings
HDFS_HOST = 'hdfs://hdfs-namenode:8020'
HDFS_LIVE_PATH = '/live'
HDFS_HISTORICAL_PATH = '/historical'
HDFS_SCHEDULED_PATH = '/scheduled'

# Database settings
MYSQL_CONN = 'mysql+mysqlconnector://airflow:airflow@mysql:3306/court_db'
MONGO_HOST = 'mongodb:27017'
MONGO_DB = 'court_db'

# ClickHouse settings
CLICKHOUSE_HOST = 'clickhouse:8123'
CLICKHOUSE_DB = 'court_analytics'

# Scoring weights for priority calculation
SCORING_WEIGHTS = {
    'alpha': 0.4,  # undertrial weight
    'beta': 0.3,   # vulnerability weight
    'gamma': 0.2,  # last hearing gap weight
    'delta': 0.1   # urgency score weight
}

# Airflow settings
AIRFLOW_DAG_DEFAULT_ARGS = {
    'owner': 'court_pipeline',
    'retries': 2,
    'retry_delay': 300  # seconds
}