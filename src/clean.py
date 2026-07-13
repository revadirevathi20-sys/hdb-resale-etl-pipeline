import pandas as pd
import numpy as np
from datetime import date

def profile_data(df):
    """Requirement 2"""
    print("=== DATA PROFILING ===")

    print(f"Shape: {df.shape}")

    print("\nNull counts:")
    print(df.isnull().sum())

    print("\nDtypes:")
    print(df.dtypes)

    print(f"\nDuplicates: {df.duplicated().sum()}")

    print("\nNumeric summary:")
    print(df.describe())

    for col in df.select_dtypes(include="object").columns:
        values = (
            df[col]
            .dropna()
            .astype(str)
            .unique()
        )

        print(f"\n[{col}] Unique values ({len(values)}):")
        print(sorted(values)[:20])

def validate_fields(df):
    """Requirement 3"""
    failed_rows = []

    # --- Date validation ---
    valid_date_mask = df["month"].notna()
    # month should be between Jan 2012 and Dec 2016
    valid_date_mask &= (df["month"] >= pd.Timestamp("2012-01-01"))
    valid_date_mask &= (df["month"] <= pd.Timestamp("2016-12-31"))

    # --- Town validation ---
    valid_towns = {
        "ANG MO KIO", "BEDOK", "BISHAN", "BUKIT BATOK", "BUKIT MERAH",
        "BUKIT PANJANG", "BUKIT TIMAH", "CENTRAL AREA", "CHOA CHU KANG",
        "CLEMENTI", "GEYLANG", "HOUGANG", "JURONG EAST", "JURONG WEST",
        "KALLANG/WHAMPOA", "MARINE PARADE", "PASIR RIS", "PUNGGOL",
        "QUEENSTOWN", "SEMBAWANG", "SENGKANG", "SERANGOON", "TAMPINES",
        "TOA PAYOH", "WOODLANDS", "YISHUN"
    }
    valid_town_mask = df["town"].str.upper().isin(valid_towns)

    # --- Flat Type validation ---
    valid_flat_types = {
        "1 ROOM", "2 ROOM", "3 ROOM", "4 ROOM", "5 ROOM",
        "EXECUTIVE", "MULTI-GENERATION", "MULTI GENERATION"
    }
    valid_flat_type_mask = df["flat_type"].str.upper().isin(valid_flat_types)

    # --- Flat Model validation ---
    valid_flat_models = {
        "IMPROVED", "NEW GENERATION", "MODEL A", "STANDARD", "SIMPLIFIED",
        "MODEL A-MAISONETTE", "MAISONETTE", "APARTMENT", "TERRACE",
        "ADJOINED FLAT", "TYPE S1", "TYPE S2", "DBSS", "MODEL A2",
        "PREMIUM APARTMENT", "PREMIUM MAISONETTE", "MULTI GENERATION",
        "PREMIUM APARTMENT LOFT", "2-ROOM", "3GEN", "IMPROVED-MAISONETTE"
    }
    valid_flat_model_mask = df["flat_model"].str.upper().isin(valid_flat_models)

    # --- storey_range validation (format: "XX TO YY") ---
    storey_pattern = r"^\d{2} TO \d{2}$"
    valid_storey_mask = df["storey_range"].str.match(storey_pattern, na=False)

    # Combine all masks
    all_valid = (
        valid_date_mask &
        valid_town_mask &
        valid_flat_type_mask &
        valid_flat_model_mask &
        valid_storey_mask
    )

    failed = df[~all_valid].copy()
    failed["fail_reason"] = ""
    failed.loc[~valid_date_mask, "fail_reason"] += "invalid_date;"
    failed.loc[~valid_town_mask, "fail_reason"] += "invalid_town;"
    failed.loc[~valid_flat_type_mask, "fail_reason"] += "invalid_flat_type;"
    failed.loc[~valid_flat_model_mask, "fail_reason"] += "invalid_flat_model;"
    failed.loc[~valid_storey_mask, "fail_reason"] += "invalid_storey_range;"

    passed = df[all_valid].copy()
    print(f"Validation: {len(passed)} passed, {len(failed)} failed")
    return passed, failed

def compute_remaining_lease(df):
    """Requirement 4"""
    df["lease_commence_date"] = pd.to_numeric(df["lease_commence_date"], errors="coerce")
    df["lease_end_year"] = df["lease_commence_date"] + 99

    def calc_remaining(row):
        if pd.isna(row["lease_end_year"]) or pd.isna(row["month"]):
            return None
        transaction_date = row["month"].date()
        end_date = date(int(row["lease_end_year"]), 1, 1)
        delta_days = (end_date - transaction_date).days
        if delta_days <= 0:
            return "0 Years 0 Months"
        years = delta_days // 365
        remaining_days = delta_days % 365
        months = remaining_days // 30
        return f"{years} Years {months} Months"

    df["remaining_lease_computed"] = df.apply(calc_remaining, axis=1)
    return df

def handle_duplicate_keys(df):
    """Requirement 5"""
    key_cols = [c for c in df.columns if c != "resale_price"]

    # Sort so highest price comes first, then drop duplicates keeping first (highest)
    df_sorted = df.sort_values("resale_price", ascending=False)
    duplicates_mask = df_sorted.duplicated(subset=key_cols, keep="first")

    failed_dupes = df_sorted[duplicates_mask].copy()
    failed_dupes["fail_reason"] = "duplicate_key_lower_price"

    passed = df_sorted[~duplicates_mask].copy()
    print(f"Duplicates: {len(failed_dupes)} removed, {len(passed)} kept")
    return passed, failed_dupes

def flag_anomalous_prices(df):
    """
    Requirement 6
    Assumptions:
    - Group by flat_type and town to compute mean and std of resale_price
    - Flag records where resale_price is more than 3 standard deviations
      from the group mean
    - flag records where resale_price <= 10,000
    - Prices within 3 std devs are considered normal for that
      flat type and town combination. Extreme outliers may indicate data errors
      or exceptional transactions, both of which warrant review.
    """
    df = df.copy()
    group_stats = df.groupby(["flat_type", "town"])["resale_price"].agg(["mean", "std"]).reset_index()
    group_stats.columns = ["flat_type", "town", "price_mean", "price_std"]
    df = df.merge(group_stats, on=["flat_type", "town"], how="left")

    df["price_zscore"] = (df["resale_price"] - df["price_mean"]) / df["price_std"].replace(0, np.nan)

    anomaly_mask = (df["price_zscore"].abs() > 3) | (df["resale_price"] <= 10000)

    failed_anomalies = df[anomaly_mask].copy()
    failed_anomalies["fail_reason"] = "anomalous_price"

    passed = df[~anomaly_mask].copy()
    passed = passed.drop(columns=["price_mean", "price_std", "price_zscore"])
    failed_anomalies = failed_anomalies.drop(columns=["price_mean", "price_std", "price_zscore"])

    print(f"Anomalous prices: {len(failed_anomalies)} flagged, {len(passed)} retained")
    return passed, failed_anomalies

def additional_cleaning(df):
    """
    Requirement 7
    - Strip whitespace from string columns.
    - Standardise town and flat_type to uppercase.
    - Ensure resale_price is numeric and positive.
    - Ensure floor_area_sqm is numeric and within plausible range (20–400 sqm).
    """
    failed = pd.DataFrame()

    # Standardise strings
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip().str.upper()

    # Numeric checks
    df["resale_price"] = pd.to_numeric(df["resale_price"], errors="coerce")
    df["floor_area_sqm"] = pd.to_numeric(df["floor_area_sqm"], errors="coerce")

    invalid_mask = (
        df["resale_price"].isna() |
        (df["resale_price"] <= 0) |
        df["floor_area_sqm"].isna() |
        (df["floor_area_sqm"] < 20) |
        (df["floor_area_sqm"] > 400)
    )

    failed = df[invalid_mask].copy()
    failed["fail_reason"] = "additional_cleaning_failed"
    passed = df[~invalid_mask].copy()

    print(f"Additional cleaning: {len(failed)} removed, {len(passed)} retained")
    return passed, failed
