# streaming_to_hdfs/kafka_to_hdfs_consumer.py
"""
Consume case data from Kafka and write to HDFS /live/YYYY/MM/DD/.
"""

from kafka import KafkaConsumer
from hdfs import InsecureClient
from config.config import KAFKA_BOOTSTRAP_SERVERS, KAFKA_TOPIC_CASES, HDFS_HOST, HDFS_LIVE_PATH
from datetime import datetime
import json

def consume_to_hdfs():
    """Consume from Kafka and write to HDFS."""
    try:
        consumer = KafkaConsumer(
            KAFKA_TOPIC_CASES,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
        )
        hdfs_client = InsecureClient(HDFS_HOST, user='hdfs')
        date_str = datetime.now().strftime("%Y/%m/%d")
        
        for message in consumer:
            case = message.value
            case_id = case['case_id']
            path = f"{HDFS_LIVE_PATH}/{date_str}/{case_id}.json"
            with hdfs_client.write(path) as f:
                f.write(json.dumps(case))
            print(f"Wrote case {case_id} to {path}")
    except Exception as e:
        print(f"Error consuming to HDFS: {e}")
        raise

if __name__ == "__main__":
    consume_to_hdfs()