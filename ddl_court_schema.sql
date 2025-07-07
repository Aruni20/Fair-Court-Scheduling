
-- Court Table
CREATE TABLE Court (
    court_id SERIAL PRIMARY KEY,
    court_name VARCHAR(100) NOT NULL,
    location VARCHAR(100),
    level VARCHAR(50),
    specialization VARCHAR(100)
);

-- Judge Table
CREATE TABLE Judge (
    judge_id SERIAL PRIMARY KEY,
    full_name VARCHAR(100) NOT NULL,
    date_of_birth DATE,
    specialization VARCHAR(100)
);

-- Judge_History Table
CREATE TABLE Judge_History (
    judge_id INT REFERENCES Judge(judge_id),
    court_id INT REFERENCES Court(court_id),
    start_date DATE,
    end_date DATE,
    PRIMARY KEY (judge_id, court_id, start_date)
);

-- Lawyer Table
CREATE TABLE Lawyer (
    lawyer_id SERIAL PRIMARY KEY,
    full_name VARCHAR(100),
    bar_registration_number VARCHAR(50) UNIQUE,
    lawyer_type VARCHAR(50)
);

-- Party Table
CREATE TABLE Party (
    party_id SERIAL PRIMARY KEY,
    full_name VARCHAR(100),
    party_type VARCHAR(50)
);

-- Case_Type Table
CREATE TABLE Case_Type (
    case_type_id SERIAL PRIMARY KEY,
    type_name VARCHAR(50) UNIQUE
);

-- Case Table
CREATE TABLE Case (
    case_id SERIAL PRIMARY KEY,
    case_number VARCHAR(50) UNIQUE,
    filing_date DATE,
    case_type_id INT REFERENCES Case_Type(case_type_id),
    court_id INT REFERENCES Court(court_id),
    is_undertrial BOOLEAN,
    vulnerability_index FLOAT,
    urgency_score FLOAT,
    status VARCHAR(50),
    estimated_duration_blocks INT,
    parent_case_id INT REFERENCES Case(case_id)
);

-- Case_Parties Table
CREATE TABLE Case_Parties (
    case_id INT REFERENCES Case(case_id),
    party_id INT REFERENCES Party(party_id),
    PRIMARY KEY (case_id, party_id)
);

-- Case_Lawyer_Assignment Table
CREATE TABLE Case_Lawyer_Assignment (
    case_id INT REFERENCES Case(case_id),
    lawyer_id INT REFERENCES Lawyer(lawyer_id),
    start_date DATE,
    end_date DATE,
    PRIMARY KEY (case_id, lawyer_id, start_date)
);

-- Case_Document Table
CREATE TABLE Case_Document (
    doc_id SERIAL PRIMARY KEY,
    case_id INT REFERENCES Case(case_id),
    document_type VARCHAR(50),
    file_path_or_mongo_id VARCHAR(255),
    version INT,
    uploaded_at TIMESTAMP
);

-- Case_Hearing Table
CREATE TABLE Case_Hearing (
    hearing_id SERIAL PRIMARY KEY,
    case_id INT REFERENCES Case(case_id),
    hearing_date DATE,
    judge_id INT REFERENCES Judge(judge_id),
    outcome VARCHAR(100),
    remarks TEXT,
    hearing_mode VARCHAR(50)
);

-- Schedule_Log Table
CREATE TABLE Schedule_Log (
    schedule_id SERIAL PRIMARY KEY,
    case_id INT REFERENCES Case(case_id),
    judge_id INT REFERENCES Judge(judge_id),
    court_id INT REFERENCES Court(court_id),
    scheduled_date DATE,
    start_time TIME,
    end_time TIME,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Court_Holidays Table
CREATE TABLE Court_Holidays (
    holiday_date DATE PRIMARY KEY,
    description VARCHAR(255)
);

-- Judge_Leave Table
CREATE TABLE Judge_Leave (
    judge_id INT REFERENCES Judge(judge_id),
    leave_date DATE,
    reason VARCHAR(255),
    PRIMARY KEY (judge_id, leave_date)
);

-- Case_Court_History Table
CREATE TABLE Case_Court_History (
    case_id INT REFERENCES Case(case_id),
    court_id INT REFERENCES Court(court_id),
    start_date DATE,
    end_date DATE,
    PRIMARY KEY (case_id, court_id, start_date)
);
