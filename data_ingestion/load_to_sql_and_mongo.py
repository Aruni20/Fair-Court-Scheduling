# data_ingestion/load_to_sql_and_mongo.py
"""
Load case metadata to MySQL and documents to MongoDB.
"""

import mysql.connector
from pymongo import MongoClient
from config.config import MYSQL_CONN, MONGO_HOST, MONGO_DB

def load_case_to_mysql(case):
    """Load case metadata to MySQL."""
    try:
        conn = mysql.connector.connect(
            host="mysql",
            user="airflow",
            password="airflow",
            database="court_db"
        )
        cursor = conn.cursor()
        
        # Insert into Case table
        cursor.execute("""
            INSERT INTO Case (case_number, filing_date, case_type_id, court_id, 
                            is_undertrial, vulnerability_index, urgency_score, status, 
                            estimated_duration_blocks, parent_case_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            case['case_number'], case['filing_date'], case['case_type_id'], case['court_id'],
            case['is_undertrial'], case['vulnerability_index'], case['urgency_score'],
            case['status'], case['estimated_duration_blocks'], case['parent_case_id']
        ))
        
        # Get inserted case_id
        case_id = cursor.lastrowid
        
        # Insert parties
        for party in case['parties']:
            cursor.execute("INSERT INTO Party (full_name, party_type) VALUES (%s, %s)",
                         (party['full_name'], party['party_type']))
            party_id = cursor.lastrowid
            cursor.execute("INSERT INTO Case_Parties (case_id, party_id) VALUES (%s, %s)",
                         (case_id, party_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        return case_id
    except Exception as e:
        print(f"Error loading to MySQL: {e}")
        raise

def load_documents_to_mongo(case, case_id):
    """Load case documents to MongoDB."""
    try:
        client = MongoClient(MONGO_HOST)
        db = client[MONGO_DB]
        collection = db['case_documents']
        
        for doc in case['documents']:
            doc['case_id'] = case_id
            collection.insert_one(doc)
        
        client.close()
        print(f"Loaded documents for case {case_id} to MongoDB")
    except Exception as e:
        print(f"Error loading to MongoDB: {e}")
        raise

def load_case(case):
    """Load case to MySQL and MongoDB."""
    case_id = load_case_to_mysql(case)
    load_documents_to_mongo(case, case_id)
    return case_id

if __name__ == "__main__":
    from faker_case_generator import generate_case_data
    cases = generate_case_data(1)
    for case in cases:
        case_id = load_case(case)
        print(f"Loaded case {case_id}")