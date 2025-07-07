# data_ingestion/kafka_producer.py
"""
Stream case data to Kafka topics for real-time processing.
"""

from kafka import KafkaProducer
import json
from config.config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC_CASES

def send_to_kafka(case):
    """Send case data to Kafka."""
    try:
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )
        
        producer.send(KAFKA_TOPIC_CASES, value=case)
        producer.flush()
        print(f"Sent case {case['case_number']} to Kafka topic {KAFKA_TOPIC_CASES}")
    except Exception as e:
        print(f"Error sending to Kafka: {e}")
        raise

if __name__ == "__main__":
    from faker_case_generator import generate_case_data
    cases = generate_case_data(1)
    for case in cases:
        send_to_kafka(case)