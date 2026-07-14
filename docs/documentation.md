# HDB Resale ETL Pipeline Documentation

## Overview

This project implements an Extract, Transform and Load (ETL) pipeline for the Singapore HDB resale dataset covering **January 2012 to December 2016**.

The pipeline performs the following stages:

1. Data ingestion
2. Data profiling
3. Data validation
4. Data cleaning
5. Data transformation
6. Hashing of identifiers
7. Output generation

The pipeline produces five groups of output datasets:

* **Raw** – Raw dataset
* **Combined** – Combined raw dataset
* **Cleaned** – Dataset after data quality checks
* **Transformed** – Dataset with the generated Resale Identifier
* **Hashed** – Transformed dataset with the hashed identifier
* **Failed** – Records removed during each stage of the ETL process

---

# Folder Structure

```
hdb-resale-etl-pipeline/
│
├── data/
│   ├── raw/
│   ├── combined/
│   ├── cleaned/
│   ├── transformed/
│   ├── hashed/
│   └── failed/
│
└── src/
    ├── ingest.py
    ├── clean.py
    ├── transform.py
    └── pipeline.py
```

---

# Prerequisites

The project requires:

* Python 3.9 or later

Install the required packages:

```bash
pip install pandas numpy
```

---

# Running the Pipeline

Navigate to the `src` folder and execute:

```bash
python3 pipeline.py for mac and python pipeline.py for windows
```

The pipeline will automatically create the required output directories if they do not already exist.

---

# ETL Process

## 1. Data Ingestion

The ingestion module:

* Reads all four HDB resale datasets.
* Standardises column names.
* Filters records outside the required period (January 2012 to December 2016).
* Combines the datasets into one master dataset.

Output:

```
data/combined/master_raw_combined.csv
```

---

## 2. Data Profiling

The profiling stage reports:

* Dataset dimensions
* Missing values
* Data types
* Duplicate counts
* Descriptive statistics
* Unique values for categorical columns

Profiling results are printed to the console for data quality assessment.

---

## 3. Data Validation

The following fields are validated:

* Month
* Town
* Flat Type
* Flat Model
* Storey Range

Invalid records are moved to the failed dataset with an appropriate failure reason.

---

## 4. Additional Cleaning

Additional cleaning includes:

* Trimming leading and trailing whitespace.
* Standardising text columns to uppercase.
* Validating resale price.
* Validating floor area.

Records failing these checks are stored in the failed dataset.

---

## 5. Remaining Lease Computation

The remaining lease is recomputed using the assumption that every HDB flat has a **99-year lease**.

The computation uses:

```
Lease End Year = Lease Commence Year + 99
Remaining Lease = Lease End Date − Current Date
```

The remaining lease is expressed as:

```
XX Years YY Months
```

rounded down to the nearest month.

---

## 6. Duplicate Business Keys

The business key is defined as:

> All columns except `resale_price`.

If duplicate business keys exist:

* the record with the highest resale price is retained;
* the remaining records are moved to the failed dataset.

---

## 7. Anomaly Detection

Potential anomalous resale prices are identified using two heuristics:

1. resale price more than **3 standard deviations** from the mean within each `(town, flat_type)` group;
2. resale price less than or equal to **S$10,000**.

Flagged records are stored in the failed dataset.

---

# Data Transformation

## Resale Identifier

A Resale Identifier is generated using the following specification:

| Component       | Description                                                                            |
| --------------- | -------------------------------------------------------------------------------------- |
| S               | Constant first character                                                               |
| Next 3 digits   | First three digits extracted from the block number (zero-padded)                       |
| Next 2 digits   | First two digits of the average resale price grouped by Year-Month, Town and Flat Type |
| Next 2 digits   | Transaction month                                                                      |
| Final character | First character of the Town                                                            |

Example:

```
S0192301A
```

---

## Duplicate Resale Identifiers

After generating the Resale Identifier, duplicate identifiers are removed by retaining the record with the higher resale price.

This behaviour follows the assignment requirement.

### Why duplicate identifiers occur

The Resale Identifier specified in the assignment is **not guaranteed to be unique** because it is derived only from:

* the first three digits of the block number;
* the first two digits of the grouped average resale price;
* the transaction month;
* the first character of the town.

It does **not** include attributes such as:

* street name;
* storey range;
* floor area;
* flat model;
* lease commencement year.

Consequently, multiple legitimate resale transactions can produce the same identifier. This is an expected outcome of the identifier design rather than an implementation error.

To comply with the assignment requirements, duplicate identifiers are resolved by retaining the transaction with the higher resale price and moving the remaining records to the failed dataset.

---

## Hashing Algorithm

The generated Resale Identifier is hashed using the **SHA-256** cryptographic hashing algorithm.

SHA-256 was selected because it:

* is irreversible;
* produces a fixed-length 256-bit hash;
* has an extremely low probability of collisions;
* preserves uniqueness for practical purposes;
* is widely adopted as an industry-standard secure hashing algorithm.

The original `resale_identifier` is retained in the transformed dataset, while the hashed dataset contains only the SHA-256 hash.

---

# Output Files

The pipeline produces the following outputs.

## Raw

```
data/combined/master_raw_combined.csv
```

---

## Cleaned

```
data/cleaned/hdb_resale_cleaned.csv
```

---

## Transformed

```
data/transformed/hdb_resale_transformed.csv
```

Contains:

* Resale Identifier
* SHA-256 hashed identifier

---

## Hashed

```
data/hashed/hdb_resale_hashed.csv
```

Contains:

* SHA-256 hashed identifier
* Original identifier removed

---

## Failed

```
data/failed/failed_validation.csv

data/failed/failed_cleaning.csv

data/failed/failed_duplicates.csv

data/failed/failed_anomalies.csv

data/failed/failed_transform_duplicates.csv

data/failed/failed_records.csv
```

Each failed record includes a `fail_reason` column indicating the stage at which it was rejected.

---

# Pipeline Summary

At the completion of the pipeline, the console displays a summary including:

* Original record count
* Validation failures
* Cleaning failures
* Duplicate key removals
* Anomalous price removals
* Duplicate Resale Identifier removals
* Final cleaned record count
* Final transformed record count
* Total failed records

This summary provides a complete audit trail of the ETL process.
