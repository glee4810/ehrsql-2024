DROP TABLE IF EXISTS patients;
CREATE TABLE patients 
(
    row_id INT NOT NULL PRIMARY KEY,
    subject_id INT NOT NULL UNIQUE,
    gender VARCHAR(5) NOT NULL,
    dob TIMESTAMP(0) NOT NULL,
    dod TIMESTAMP(0)
);

DROP TABLE IF EXISTS admissions;
CREATE TABLE admissions
(
    row_id INT NOT NULL PRIMARY KEY,
    subject_id INT NOT NULL,
    hadm_id INT NOT NULL UNIQUE,
    admittime TIMESTAMP(0) NOT NULL,
    dischtime TIMESTAMP(0),
    admission_type VARCHAR(50) NOT NULL,
    admission_location VARCHAR(50) NOT NULL,
    discharge_location VARCHAR(50),
    insurance VARCHAR(255) NOT NULL,
    language VARCHAR(10),
    marital_status VARCHAR(50),
    age INT NOT NULL,
    FOREIGN KEY(subject_id) REFERENCES patients(subject_id)
);

DROP TABLE IF EXISTS d_icd_diagnoses;
CREATE TABLE d_icd_diagnoses
(
    row_id INT NOT NULL PRIMARY KEY,
    icd_code VARCHAR(10) NOT NULL UNIQUE,
    long_title VARCHAR(255) NOT NULL
);

DROP TABLE IF EXISTS d_icd_procedures;
CREATE TABLE d_icd_procedures 
(
    row_id INT NOT NULL PRIMARY KEY,
    icd_code VARCHAR(10) NOT NULL UNIQUE,
    long_title VARCHAR(255) NOT NULL
);

DROP TABLE IF EXISTS d_labitems;
CREATE TABLE d_labitems 
(
    row_id INT NOT NULL PRIMARY KEY,
    itemid INT NOT NULL UNIQUE,
    label VARCHAR(200)
);

DROP TABLE IF EXISTS d_items;
CREATE TABLE d_items 
(
    row_id INT NOT NULL PRIMARY KEY,
    itemid INT NOT NULL UNIQUE,
    label VARCHAR(200) NOT NULL,
    abbreviation VARCHAR(200) NOT NULL,
    linksto VARCHAR(50) NOT NULL
);

DROP TABLE IF EXISTS diagnoses_icd;
CREATE TABLE diagnoses_icd
(
    row_id INT NOT NULL PRIMARY KEY,
    subject_id INT NOT NULL,
    hadm_id INT NOT NULL,
    icd_code VARCHAR(10) NOT NULL,
    charttime TIMESTAMP(0) NOT NULL,
    FOREIGN KEY(hadm_id) REFERENCES admissions(hadm_id),
    FOREIGN KEY(icd_code) REFERENCES d_icd_diagnoses(icd_code)
);

DROP TABLE IF EXISTS procedures_icd;
CREATE TABLE procedures_icd
(
    row_id INT NOT NULL PRIMARY KEY,
    subject_id INT NOT NULL,
    hadm_id INT NOT NULL,
    icd_code VARCHAR(10) NOT NULL,
    charttime TIMESTAMP(0) NOT NULL,
    FOREIGN KEY(hadm_id) REFERENCES admissions(hadm_id),
    FOREIGN KEY(icd_code) REFERENCES d_icd_procedures(icd_code)
);

DROP TABLE IF EXISTS labevents;
CREATE TABLE labevents
(
    row_id INT NOT NULL PRIMARY KEY,
    subject_id INT NOT NULL,
    hadm_id INT NOT NULL,
    itemid INT NOT NULL,
    charttime TIMESTAMP(0),
    valuenum DOUBLE PRECISION,
    valueuom VARCHAR(20),
    FOREIGN KEY(hadm_id) REFERENCES admissions(hadm_id),
    FOREIGN KEY(itemid) REFERENCES d_labitems(itemid)
);

DROP TABLE IF EXISTS prescriptions;
CREATE TABLE prescriptions
(
    row_id INT NOT NULL PRIMARY KEY,
    subject_id INT NOT NULL,
    hadm_id INT NOT NULL,
    starttime TIMESTAMP(0) NOT NULL,
    stoptime TIMESTAMP(0),
    drug VARCHAR(255) NOT NULL,
    dose_val_rx VARCHAR(100) NOT NULL,
    dose_unit_rx VARCHAR(50) NOT NULL,
    route VARCHAR(50) NOT NULL,
    FOREIGN KEY(hadm_id) REFERENCES admissions(hadm_id)
);

DROP TABLE IF EXISTS cost;
CREATE TABLE cost
(
    row_id INT NOT NULL PRIMARY KEY,
    subject_id INT NOT NULL,
    hadm_id INT NOT NULL,
    event_type VARCHAR(20) NOT NULL,
    event_id INT NOT NULL,
    chargetime TIMESTAMP(0) NOT NULL,
    cost DOUBLE PRECISION NOT NULL,
    FOREIGN KEY(hadm_id) REFERENCES admissions(hadm_id),
    FOREIGN KEY(event_id) REFERENCES diagnoses_icd(row_id),
    FOREIGN KEY(event_id) REFERENCES procedures_icd(row_id),
    FOREIGN KEY(event_id) REFERENCES labevents(row_id),
    FOREIGN KEY(event_id) REFERENCES prescriptions(row_id)  
);

DROP TABLE IF EXISTS chartevents;
CREATE TABLE chartevents
(
    row_id INT NOT NULL PRIMARY KEY,
    subject_id INT NOT NULL,
    hadm_id INT NOT NULL,
    stay_id INT NOT NULL,
    itemid INT NOT NULL,
    charttime TIMESTAMP(0) NOT NULL,
    valuenum DOUBLE PRECISION,
    valueuom VARCHAR(50),
    FOREIGN KEY(hadm_id) REFERENCES admissions(hadm_id),
    FOREIGN KEY(stay_id) REFERENCES icustays(stay_id),
    FOREIGN KEY(itemid) REFERENCES d_items(itemid)
);

DROP TABLE IF EXISTS inputevents;
CREATE TABLE inputevents
(
    row_id INT NOT NULL PRIMARY KEY,
    subject_id INT NOT NULL,
    hadm_id INT NOT NULL,
    stay_id INT NOT NULL,
    starttime TIMESTAMP(0) NOT NULL,
    itemid INT NOT NULL,
    totalamount DOUBLE PRECISION,
    totalamountuom VARCHAR(50),
    FOREIGN KEY(hadm_id) REFERENCES admissions(hadm_id),
    FOREIGN KEY(stay_id) REFERENCES icustays(stay_id),
    FOREIGN KEY(itemid) REFERENCES d_items(itemid)
);

DROP TABLE IF EXISTS outputevents;
CREATE TABLE outputevents
(
    row_id INT NOT NULL PRIMARY KEY,
    subject_id INT NOT NULL,
    hadm_id INT NOT NULL,
    stay_id INT NOT NULL,
    charttime TIMESTAMP(0) NOT NULL,
    itemid INT NOT NULL,
    value DOUBLE PRECISION,
    valueuom VARCHAR(50),
    FOREIGN KEY(hadm_id) REFERENCES admissions(hadm_id),
    FOREIGN KEY(stay_id) REFERENCES icustays(stay_id),
    FOREIGN KEY(itemid) REFERENCES d_items(itemid)
);

DROP TABLE IF EXISTS microbiologyevents;
CREATE TABLE microbiologyevents
(
    row_id INT NOT NULL PRIMARY KEY,
    subject_id INT NOT NULL,
    hadm_id INT NOT NULL,
    charttime TIMESTAMP(0) NOT NULL,
    spec_type_desc VARCHAR(100),
    test_name VARCHAR(100),
    org_name VARCHAR(100),
    FOREIGN KEY(hadm_id) REFERENCES admissions(hadm_id)
);

DROP TABLE IF EXISTS icustays;
CREATE TABLE icustays
(
    row_id INT NOT NULL PRIMARY KEY,
    subject_id INT NOT NULL,
    hadm_id INT NOT NULL,
    stay_id INT NOT NULL UNIQUE,
    first_careunit VARCHAR(20) NOT NULL,
    last_careunit VARCHAR(20) NOT NULL,
    intime TIMESTAMP(0) NOT NULL,
    outtime TIMESTAMP(0),
    FOREIGN KEY(hadm_id) REFERENCES admissions(hadm_id)
);

DROP TABLE IF EXISTS transfers;
CREATE TABLE transfers
(
    row_id INT NOT NULL PRIMARY KEY,
    subject_id INT NOT NULL,
    hadm_id INT NOT NULL,
    transfer_id INT NOT NULL,
    eventtype VARCHAR(20) NOT NULL,
    careunit VARCHAR(20),
    intime TIMESTAMP(0) NOT NULL,
    outtime TIMESTAMP(0),
    FOREIGN KEY(hadm_id) REFERENCES admissions(hadm_id)
);