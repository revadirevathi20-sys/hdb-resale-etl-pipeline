import os
import pandas as pd

from ingest import combine_datasets
from clean import (
    profile_data,
    validate_fields,
    compute_remaining_lease,
    handle_duplicate_keys,
    flag_anomalous_prices,
    additional_cleaning
)
from transform import (
    create_resale_identifier,
    handle_transform_duplicates,
    hash_identifier
)


def ensure_directories():
    """Create output folders if they do not exist."""
    os.makedirs("../data/raw", exist_ok=True)
    os.makedirs("../data/cleaned", exist_ok=True)
    os.makedirs("../data/transformed", exist_ok=True)
    os.makedirs("../data/hashed", exist_ok=True)
    os.makedirs("../data/failed", exist_ok=True)


def run_pipeline():

    ensure_directories()

    failed_records = []

    # =====================================================
    # INGESTION
    # =====================================================
    print("\n========== INGESTION ==========\n")

    master = combine_datasets()

    original_records = len(master)

    master.to_csv(
        "../data/raw/master_raw_combined.csv",
        index=False
    )

    # =====================================================
    # DATA PROFILING
    # =====================================================
    print("\n========== DATA PROFILING ==========\n")

    profile_data(master)

    # =====================================================
    # VALIDATION
    # =====================================================
    print("\n========== VALIDATION ==========\n")

    master, failed_validation = validate_fields(master)
    failed_records.append(failed_validation)

    failed_validation.to_csv(
        "../data/failed/failed_validation.csv",
        index=False
    )

    # =====================================================
    # ADDITIONAL CLEANING
    # =====================================================
    print("\n========== ADDITIONAL CLEANING ==========\n")

    master, failed_cleaning = additional_cleaning(master)
    failed_records.append(failed_cleaning)

    failed_cleaning.to_csv(
        "../data/failed/failed_cleaning.csv",
        index=False
    )

    # =====================================================
    # COMPUTE REMAINING LEASE
    # =====================================================
    print("\n========== COMPUTE REMAINING LEASE ==========\n")

    master = compute_remaining_lease(master)

    # =====================================================
    # DUPLICATE HANDLING
    # =====================================================
    print("\n========== DUPLICATE HANDLING ==========\n")

    master, failed_duplicates = handle_duplicate_keys(master)
    failed_records.append(failed_duplicates)

    failed_duplicates.to_csv(
        "../data/failed/failed_duplicates.csv",
        index=False
    )

    # =====================================================
    # ANOMALY DETECTION
    # =====================================================
    print("\n========== ANOMALY DETECTION ==========\n")

    master, failed_anomalies = flag_anomalous_prices(master)
    failed_records.append(failed_anomalies)

    failed_anomalies.to_csv(
        "../data/failed/failed_anomalies.csv",
        index=False
    )

    # =====================================================
    # SAVE CLEANED DATA
    # =====================================================
    master.to_csv(
        "../data/cleaned/hdb_resale_cleaned.csv",
        index=False
    )

    # =====================================================
    # TRANSFORMATION
    # =====================================================
    print("\n========== TRANSFORMATION ==========\n")

    transformed = create_resale_identifier(master)

    transformed, failed_transform = handle_transform_duplicates(transformed)
    failed_records.append(failed_transform)

    failed_transform.to_csv(
        "../data/failed/failed_transform_duplicates.csv",
        index=False
    )

    transformed = hash_identifier(transformed)

    transformed = transformed.sort_values(
        ["month", "town", "block"]
    )

    transformed.to_csv(
        "../data/transformed/hdb_resale_transformed.csv",
        index=False
    )

    # =====================================================
    # HASHED OUTPUT
    # =====================================================
    hashed = transformed.copy()

    hashed = hashed.drop(columns=["resale_identifier"])

    hashed.to_csv(
        "../data/hashed/hdb_resale_hashed.csv",
        index=False
    )

    # =====================================================
    # COMBINED FAILED RECORDS
    # =====================================================
    all_failed = pd.concat(
        failed_records,
        ignore_index=True
    )

    all_failed = all_failed.drop_duplicates()

    all_failed.to_csv(
        "../data/failed/failed_records.csv",
        index=False
    )

    # =====================================================
    # SUMMARY
    # =====================================================
    print("\n========== PIPELINE SUMMARY ==========\n")

    print(f"Original records           : {original_records:,}")
    print(f"Validation failures        : {len(failed_validation):,}")
    print(f"Additional cleaning        : {len(failed_cleaning):,}")
    print(f"Duplicate failures         : {len(failed_duplicates):,}")
    print(f"Anomaly failures           : {len(failed_anomalies):,}")
    print(f"Transform duplicates       : {len(failed_transform):,}")
    print(f"Final cleaned records      : {len(master):,}")
    print(f"Final transformed records  : {len(transformed):,}")
    print(f"Total failed records       : {len(all_failed):,}")

    print("\nOutput files created:")
    print("../data/raw/master_raw_combined.csv")
    print("../data/cleaned/hdb_resale_cleaned.csv")
    print("../data/transformed/hdb_resale_transformed.csv")
    print("../data/hashed/hdb_resale_hashed.csv")

    print("../data/failed/failed_validation.csv")
    print("../data/failed/failed_cleaning.csv")
    print("../data/failed/failed_duplicates.csv")
    print("../data/failed/failed_anomalies.csv")
    print("../data/failed/failed_transform_duplicates.csv")
    print("../data/failed/failed_records.csv")

    print("\nPipeline completed successfully.")

if __name__ == "__main__":
    run_pipeline()
