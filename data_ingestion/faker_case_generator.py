# data_ingestion/faker_case_generator.py
"""
Generate synthetic case data using Faker to simulate court filings.
"""

from faker import Faker
import random
from datetime import datetime, timedelta

def generate_case_data(num_cases=1):
    """Generate synthetic case data."""
    fake = Faker()
    cases = []
    
    for _ in range(num_cases):
        case = {
            'case_id': fake.unique.uuid4(),
            'case_number': fake.unique.bothify(text='C####'),
            'filing_date': (datetime.now() - timedelta(days=random.randint(0, 365))).date(),
            'case_type_id': random.randint(1, 5),  # Matches Case_Type table
            'court_id': random.randint(1, 10),     # Matches Court table
            'is_undertrial': random.choice([True, False]),
            'vulnerability_index': round(random.uniform(0, 1), 2),
            'urgency_score': round(random.uniform(0, 1), 2),
            'status': random.choice(['Pending', 'Active', 'Closed']),
            'estimated_duration_blocks': random.randint(1, 3),  # 1-3 hours
            'last_hearing_gap_days': random.randint(0, 90),    # Days since last hearing
            'parent_case_id': None,
            'parties': [
                {'party_id': random.randint(1, 100), 'full_name': fake.name(), 'party_type': 'Plaintiff'},
                {'party_id': random.randint(1, 100), 'full_name': fake.name(), 'party_type': 'Defendant'}
            ],
            'documents': [
                {
                    'doc_id': fake.unique.uuid4(),
                    'document_type': random.choice(['Affidavit', 'Petition', 'Evidence']),
                    'content': fake.text(max_nb_chars=200),
                    'version': 1,
                    'uploaded_at': datetime.now()
                }
            ]
        }
        cases.append(case)
    
    return cases

if __name__ == "__main__":
    sample_cases = generate_case_data(2)
    for case in sample_cases:
        print(case)