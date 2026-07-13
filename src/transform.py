import pandas as pd
import hashlib

def create_resale_identifier(df):
    """
    Transformation Requirement 1: Create Resale Identifier
    """
    df = df.copy()

    # --- Part 1: First character ---
    df["id_part1"] = "S"

    # --- Part 2: First 3 digits of block ---
    df["block_digits"] = df["block"].str.extract(r"(\d+)")[0].fillna("0")
    df["id_part2"] = df["block_digits"].str[:3].str.zfill(3)

    # --- Part 3: First 2 digits of avg resale price by year-month, town, flat_type ---
    df["year_month"] = df["month"].dt.to_period("M").astype(str)
    avg_price = (
        df.groupby(["year_month", "town", "flat_type"])["resale_price"]
        .mean()
        .reset_index()
        .rename(columns={"resale_price": "avg_price"})
    )
    df = df.merge(avg_price, on=["year_month", "town", "flat_type"], how="left")
    df["id_part3"] = df["avg_price"].fillna(0).astype(int).astype(str).str[:2].str.zfill(2)

    # --- Part 4: 2-digit month ---
    df["id_part4"] = df["month"].dt.month.astype(str).str.zfill(2)

    # --- Part 5: First character of town ---
    df["id_part5"] = df["town"].str.strip().str.upper().str[0]

    # Combine into Resale Identifier
    df["resale_identifier"] = (
        df["id_part1"] +
        df["id_part2"] +
        df["id_part3"] +
        df["id_part4"] +
        df["id_part5"]
    )

    # Drop helper columns
    df = df.drop(columns=["id_part1", "id_part2", "id_part3", "id_part4",
                           "id_part5", "block_digits", "year_month", "avg_price"])
    return df

def handle_transform_duplicates(df):
    """Transformation Requirement 2"""
    df_sorted = df.sort_values("resale_price", ascending=False)
    failed = df_sorted[df_sorted.duplicated(subset=["resale_identifier"], keep="first")].copy()
    failed["fail_reason"] = "transform_duplicate_identifier"
    passed = df_sorted[~df_sorted.duplicated(subset=["resale_identifier"], keep="first")].copy()
    print(f"Transform duplicates: {len(failed)} removed, {len(passed)} kept")
    return passed, failed

# def hash_identifier(df):
#     """
#     Transformation Requirement 3: Hash the resale_identifier using SHA-256
#     """
#     def sha256_hash(value):
#         return hashlib.sha256(str(value).encode("utf-8")).hexdigest()

#     df = df.copy()

#     df["resale_identifier_hashed"] = (
#         df["resale_identifier"]
#         .apply(sha256_hash)
#     )

#     # Remove the original identifier after hashing
#     df = df.drop(columns=["resale_identifier"])

#     return df
def hash_identifier(df):
    """
    Transformation Requirement 3: Hash the resale_identifier using SHA-256
    """
    def sha256_hash(value):
        return hashlib.sha256(str(value).encode("utf-8")).hexdigest()

    df = df.copy()
    df["resale_identifier_hashed"] = df["resale_identifier"].apply(sha256_hash)

    return df
    
if __name__ == "__main__":

    os.makedirs("../data/transformed", exist_ok=True)

    df = pd.read_csv(
        "../data/cleaned/hdb_resale_cleaned.csv",
        low_memory=False
    )

    df["month"] = pd.to_datetime(df["month"])

    print("\n========== START TRANSFORMATION ==========\n")

    # Requirement 1
    df = create_resale_identifier(df)

    # Requirement 2
    passed, failed_duplicates = handle_transform_duplicates(df)

    # Requirement 3
    passed = hash_identifier(passed)
    # Sort final dataset for readability
    passed = passed.sort_values(
        ["month", "town", "block"]
    )

    # Save outputs
    passed.to_csv(
        "../data/transformed/hdb_resale_transformed.csv",
        index=False
    )

    failed_duplicates.to_csv(
        "../data/transformed/failed_transform_duplicates.csv",
        index=False
    )

    print("\n========== TRANSFORMATION SUMMARY ==========")
    print(f"Input records               : {len(df):,}")
    print(f"Duplicate identifiers       : {len(failed_duplicates):,}")
    print(f"Final transformed records   : {len(passed):,}")

    print("\nFiles saved:")
    print("../data/transformed/hdb_resale_transformed.csv")
    print("../data/transformed/failed_transform_duplicates.csv")
