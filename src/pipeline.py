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
    # ADDITIONAL CLEANING
    # =====================================================
    print("\n========== ADDITIONAL CLEANING ==========\n")

    master, failed_cleaning = additional_cleaning(master)
    failed_records.append(failed_cleaning)

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
    hashed = transformed.copy()

    hashed = hashed.drop(columns=["resale_identifier"])

    hashed.to_csv(
        "../data/hashed/hdb_resale_hashed.csv",
        index=False
    )

    # =====================================================
    # FAILED RECORDS
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

    print(f"Original records           : {len(master) + len(all_failed):,}")
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
    print("../data/failed/failed_records.csv")

    print("\nPipeline completed successfully.")
