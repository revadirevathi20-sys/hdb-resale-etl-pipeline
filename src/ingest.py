import pandas as pd
import os

RAW_DIR = "data/raw/"

# Map each file to its date filter
FILE_CONFIG = [
    {
        "filename": "resale-flat-prices-based-on-approval-date-2000-feb-2012.csv",
        "date_col": "month",          
        "filter_from": "2012-01",     
    },
    {
        "filename": "resale-flat-prices-based-on-approval-date-mar-2012-to-dec-2014.csv",
        "date_col": "month",
        "filter_from": None,          
    },
    {
        "filename": "resale-flat-prices-based-on-registration-date-from-jan-2015-to-dec-2016.csv",
        "date_col": "month",
        "filter_from": None,
    },
    {
        "filename": "resale-flat-prices-based-on-registration-date-from-jan-2017-onwards.csv",
        "date_col": "month",
        "filter_from": None,
    },
]

def load_and_filter(config):
    filepath = os.path.join(RAW_DIR, config["filename"])
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
    print(f"\nMaster dataset shape: {master.shape}")
    return master

if __name__ == "__main__":
    master_df = combine_datasets()
    master_df.to_csv("data/cleaned/master_raw_combined.csv", index=False)
    print("Master dataset saved.")
