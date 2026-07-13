# HDB Resale ETL Pipeline — Documentation

## Overview

This project implements an end-to-end ETL (Extract, Transform, Load) pipeline for HDB resale flat. The pipeline ingests raw CSV files, profiles and validates the data, cleans and transforms it, and outputs a final dataset ready for analysis.

---

## Project Structure
hdb-resale-etl/
├── data/
│   ├── raw/            # Raw CSV files downloaded from data.gov.sg
│   ├── cleaned/        # Data after cleaning (nulls, duplicates, formats fixed)
│   ├── transformed/    # Data after transformation (new columns, standardisation)
│   ├── failed/         # Rows that failed validation checks
│   └── hashed/         # Deduplication hashes
├── src/
│   ├── ingest.py       # Downloads and combines raw data filests
│   ├── clean.py        # Cleans invalid or malformed data
│   ├── transform.py    # Applies business transformations
│   └── output.py       # Writes final output to file
├── notebooks/
│   └── eda.ipynb       # Exploratory data analysis
├── docs/
│   └── documentation.md
├── .gitignore
├── requirements.txt
└── README.md

## Pipeline Stages

### 1. Ingest (`ingest.py`)

Downloads all available HDB resale flat price dataset API and combines them into a single raw CSV file saved to `data/raw/`.

- Output: `data/raw/master_combined_raw.csv`

### 2. Clean (`clean.py`)

Applies cleaning operations to the validated dataset, including trimming whitespace, standardising string casing, fixing date formats, and removing duplicates.

- Input: `data/cleaned/`
- Output: `data/cleaned/master_cleaned.csv`

### 3. Transform (`transform.py`)

Applies business logic transformations to enrich the cleaned dataset. New derived columns are added to support downstream analysis.

Transformations include:

- Extracting `year` and `quarter` from `month`
- Parsing `storey_range` into `storey_low` and `storey_high` integer columns
- Computing `storey_mid` as the midpoint of the storey range
- Computing `remaining_lease_years` from `lease_commence_date`
- Computing `price_per_sqm` from `resale_price` and `floor_area_sqm`

- Input: `data/cleaned/master_cleaned.csv`
- Output: `data/transformed/master_transformed.csv`

### 4. Output (`output.py`)

Writes the final transformed dataset to the output location and generates a summary report of the pipeline run, including row counts at each stage.

- Input: `data/transformed/master_transformed.csv`
- Output: final CSV and pipeline run summary

---

## Data Dictionary

| Column | Type | Description |
|---|---|---|
| `month` | string | Transaction month in `YYYY-MM` format |
| `town` | string | HDB town where the flat is located |
| `flat_type` | string | Flat type (e.g. 3 ROOM, 4 ROOM, 5 ROOM) |
| `block` | string | Block number of the flat |
| `street_name` | string | Street name of the flat |
| `storey_range` | string | Storey range in `XX TO XX` format |
| `floor_area_sqm` | float | Floor area in square metres |
| `flat_model` | string | Flat model (e.g. Improved, New Generation) |
| `lease_commence_date` | integer | Year the lease commenced |
| `remaining_lease` | string | Remaining lease in years and months (where available) |
| `resale_price` | float | Resale transaction price in SGD |
| `year` | integer | Derived from `month` |
| `quarter` | string | Derived from `month` (e.g. Q1, Q2) |
| `storey_low` | integer | Lower bound of storey range |
| `storey_high` | integer | Upper bound of storey range |
| `storey_mid` | float | Midpoint of storey range |
| `remaining_lease_years` | float | Remaining lease in years (derived) |
| `price_per_sqm` | float | Resale price divided by floor area |

---

## Assumptions and Design Decisions

- Records that fail validation are not dropped but isolated to `data/failed/` for review. This allows the pipeline to be audited and rerun after investigation.
- Deduplication is based on a hash of key fields (`month`, `block`, `street_name`, `storey_range`, `flat_type`, `resale_price`) to avoid removing legitimate repeat transactions.
- The pipeline is designed to be idempotent — running it multiple times on the same input should produce the same output.
- All string fields are uppercased and trimmed for consistency.

---

## Requirements

See `requirements.txt` for the full list of dependencies. Key libraries used:

- `pandas` — data manipulation
- `requests` — API calls to data.gov.sg
- `hashlib` — row-level deduplication hashing
- `pytest` — unit testing

---

## How to Run

```bash
# Set up environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run the full pipeline
python src/ingest.py
python src/clean.py
python src/transform.py
python src/output.py
