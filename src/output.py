import pandas as pd
from ingest import combine_datasets
from clean import (profile_data, validate_fields, compute_remaining_lease,
                   handle_duplicate_keys, flag_anomalous_prices, additional_cleaning)
from transform import create_resale_identifier, handle_transform_duplicates, hash_identifier

def run_pipeline():
    all_failed = []

    # --- INGEST ---
    print("\n=== INGESTION ===")
    master = combine_datasets()
    master.to_csv("data/raw/master_combined_raw.csv", index=False)

    # --- PROFILE ---
    print("\n=== PROFILING ===")
    profile_data(master)

    # --- ADDITIONAL CLEANING (Req 7) ---
    print("\n=== ADDITIONAL CLEANING ===")
    master, failed_cleaning = additional_cleaning(master)
    all_failed.append(failed_cleaning)

    # --- VALIDATION (Req 3) ---
    print("\n=== VALIDATION ===")
    master, failed_validation = validate_fields(master)
    all_failed.append(failed_validation)

    # --- REMAINING LEASE (Req 4) ---
    print("\n=== REMAINING LEASE ===")
    master = compute_remaining_lease(master)

    # --- DUPLICATE KEYS (Req 5) ---
    print("\n=== DUPLICATE KEY HANDLING ===")
    master, failed_dupes = handle_duplicate_keys(master)
    all_failed.append(failed_dupes)

    # --- ANOMALOUS PRICES (Req 6) ---
    print("\n=== ANOMALY DETECTION ===")
    master, failed_anomalies = flag_anomalous_prices(master)
    all_failed.append(failed_anomalies)

    # Save cleaned output
    master.to_csv("data/cleaned/cleaned_data.csv", index=False)
    print(f"\nCleaned dataset: {master.shape}")

    # --- TRANSFORMATION ---
    print("\n=== TRANSFORMATION ===")
    transformed = create_resale_identifier(master)
    transformed, failed_transform = handle_transform_duplicates(transformed)
    all_failed.append(failed_transform)
    transformed.to_csv("data/transformed/transformed_data.csv", index=False)

    # --- HASHED OUTPUT ---
    hashed = hash_identifier(transformed)
    hashed.to_csv("data/hashed/hashed_data.csv", index=False)

    # --- FAILED OUTPUT ---
    all_failed_df = pd.concat(all_failed, ignore_index=True)
    all_failed_df.to_csv("data/failed/failed_records.csv", index=False)
    print(f"\nFailed records: {len(all_failed_df)}")
    print("\nPipeline complete.")

if __name__ == "__main__":
    run_pipeline()
