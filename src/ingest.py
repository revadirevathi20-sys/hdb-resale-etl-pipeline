import pandas as pd
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

RAW_DIR = os.path.join(BASE_DIR, "..", "data", "raw")
CLEAN_DIR = os.path.join(BASE_DIR, "..", "data", "cleaned")

# Map each file to its date filter
FILE_CONFIG = [
    {
        "filename": "ResaleFlatPricesBasedonApprovalDate2000Feb2012.csv",
        "date_col": "month",          
        "filter_from": "2012-01",     
    },
    {
        "filename": "ResaleFlatPricesBasedonRegistrationDateFromMar2012toDec2014.csv",
        "date_col": "month",
        "filter_from": None,          
    },
    {
        "filename": "ResaleFlatPricesBasedonRegistrationDateFromJan2015toDec2016.csv",
        "date_col": "month",
        "filter_from": None,
    },
    {
        "filename": "ResaleflatpricesbasedonregistrationdatefromJan2017onwards.csv",
        "date_col": "month",
        "filter_from": None,
    },
]

def load_and_filter(config):
    filepath = os.path.join(RAW_DIR, config["filename"])
    print(filepath)
    print(os.path.exists(filepath))
    df = pd.read_csv(filepath)
    df["month"] = pd.to_datetime(df["month"], format="%Y-%m")

    if config["filter_from"]:
        cutoff = pd.to_datetime(config["filter_from"], format="%Y-%m")
        before_filter = len(df)
        df = df[df["month"] >= cutoff]
        after_filter = len(df)
        print(f"[{config['filename']}] Filtered out {before_filter - after_filter} rows before {config['filter_from']}")

    return df

def combine_datasets():
    frames = [load_and_filter(cfg) for cfg in FILE_CONFIG]
    master = pd.concat(frames, ignore_index=True)

    master = master[
        (master["month"] >= pd.Timestamp("2012-01-01")) &
        (master["month"] <= pd.Timestamp("2016-12-31"))
    ]

    print(f"\nMaster dataset shape: {master.shape}")
    print(f"Date range: {master['month'].min()} to {master['month'].max()}")

    return master

if __name__ == "__main__":
    master_df = combine_datasets()

    output_path = os.path.join("..", "data", "cleaned", "master_raw_combined.csv")
    master_df.to_csv(output_path, index=False)

    print(f"Master dataset saved to {output_path}")
