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

    # =====================================================
    # ANOMALY DETECTION
    # =====================================================
    print("\n========== ANOMALY DETECTION ==========\n")

    master, failed_anomalies = flag_anomalous_prices(master)
    failed_records.append(failed_anomalies)

    # =====================================================
    # ADDITIONAL CLEANING
    # =====================================================
    print("\n========== ADDITIONAL CLEANING ==========\n")

    master, failed_cleaning = additional_cleaning(master)
    failed_records.append(failed_cleaning)

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
    transformed.to_csv(
        "../data/hashed/hdb_resale_hashed.csv",
        index=False
    )

    # =====================================================
    # SAVE FAILED RECORDS
    # =====================================================
    all_failed = pd.concat(
        failed_records,
        ignore_index=True
    )

    all_failed.to_csv(
        "../data/failed/failed_records.csv",
        index=False
    )

    # =====================================================
    # SUMMARY
    # =====================================================
    print("\n========== PIPELINE SUMMARY ==========\n")

    print(f"Raw records               : {len(master) + len(all_failed):,}")
    print(f"Cleaned records           : {len(master):,}")
    print(f"Transformed records       : {len(transformed):,}")
    print(f"Failed records            : {len(all_failed):,}")

    print("\nOutput files created:")
    print("✓ ../data/raw/master_raw_combined.csv")
    print("✓ ../data/cleaned/hdb_resale_cleaned.csv")
    print("✓ ../data/transformed/hdb_resale_transformed.csv")
    print("✓ ../data/hashed/hdb_resale_hashed.csv")
    print("✓ ../data/failed/failed_records.csv")

    print("\nPipeline completed successfully.")


if __name__ == "__main__":
    run_pipeline()
